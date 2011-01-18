import logging
import httplib2
import urllib
from datetime import datetime

try:
    import simplejson as json
except ImportError:
    import json

from digg.api import Digg, Digg2
from google.appengine.ext import db

from omnigeist.activity import abstract
from omnigeist import models
from omnigeist.http_util import MemcacheFileAdapter


class RedditProvider(abstract.Activity):
    REDDIT_URL = 'http://reddit.com'

    """
    TODO:
        How to model subreddits? for now don't worry about it. understand how we
        want to use the data, first.

        Need to lookup response structure to understand how to store it.
    """

    def __init__(self, c_url):
        self.epos = self._get_or_create_epos(c_url, 'reddit')
        self.h = httplib2.Http(cache=MemcacheFileAdapter('shorturl'))

        info_url = '%s/api/info.json?%s' % (self.REDDIT_URL, 
                                            urllib.urlencode({'count': '1',
                                                              'url': c_url}))
        resp, content = self.h.request(info_url)
        if resp.status > 299:
            raise Exception("error fetching %s" % info_url)
        content = json.loads(content)

        #todo make this a dict comprehension
        self.epos.subreddits = [{'subreddit': subr['data']['subreddit'],
                                 'permalink': subr['data']['permalink'],
                                 'title': subr['data']['title'],
                                 'ups': subr['data']['ups'],
                                 'downs': subr['data']['downs']}
                                for subr in content['data']['children']]

        # http://www.reddit.com/api/info.json?count=1&url=http://voices.washingtonpost.com/blog-post/2010/12/openleaks_launches_rivals_wiki.html

    def update_events(self, start_date):
        for subr in self.epos.subreddits:
            info_url = '%s%s.json' % (self.REDDIT_URL, subr['permalink'][:-1])
            resp, content = self.h.request(info_url)
            content = json.loads(content)
            logging.info("loading comments from %s" % subr['permalink'])

            def _process_node(node):
                    created_on = datetime.utcfromtimestamp(node['created_utc'])
                    key = '_'.join(['reddit', 'comment', node['id']])
                    c = models.RedditUserComment.get_or_insert(key_name=key,
                                                               parent=self.epos,
                                                               ref_id=node['id'],
                                                               activity_created=created_on)
                    parent_key = '_'.join(['reddit', 'comment', node['parent_id'].split('_')[1]])
                    c.ups = node['ups']
                    c.downs = node['downs']
                    if node['parent_id'] != node['link_id']:
                        c.reply_to = db.Key.from_path(models.RedditUserComment.kind(),
                                                      parent_key,
                                                      parent=self.epos.key())
                    c.body = node['body']
                    c.author = node['author']
                    c.put()
            
            def _load_activity(children):
                """Operates on structures which look like this...
                {u'data': {                           // top level obj holding comments
                    u'after': None,
                    u'before': None,
                    u'kind': 'Listing',
                    u'children': [{
                        u'data': {
                            ...                        // comment info
                            u'kind': u't1',
                            u'replies': {
                                u'data': {
                                    u'after': None,
                                    u'before': None,
                                    u'children': [{
                                        u'data': {
                                            ...         // comment info
                                        },
                                        ...             // more replies
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    ...                             // more top level comment
                    ]} 
                }
                """

                if children['kind'] == 'Listing':
                    logging.info("found %d children" % len(children['data']['children']))
                    for child in children['data']['children']:
                        _load_activity(child)
                elif children['kind'] == 't1':
                    _process_node(children['data'])
                    if len(children['data']['replies']):
                        _load_activity(children['data']['replies'])

            _load_activity(content[1])


class DiggProvider(abstract.Activity):
    host = 'digg'


    def __init__(self, c_url):
        self.epos = self._get_or_create_epos(c_url, 'digg')
        digg_handle = Digg2()

        link = ",".join([self.epos.url])
        info = digg_handle.story.getInfo(links=link)
        logging.debug(info)

        if info['count'] == 0:
            raise abstract.NoActivityException()

        story = info['stories'][0]
        self.story_id = self.epos.ref_id = story['story_id']
        self.epos.diggs = story['diggs']
        self.epos.permalink = story['permalink']
        self.epos.put()


    def update_events(self, start_date):
        #TODO: Digg2 api broken for comments
        digg_handle = Digg()
        ret = digg_handle.story.getComments(story_id=self.story_id)

        count = ret['total']
        logging.debug("found %d comments" % count)
        if count == 0:
            logging.debug("no comments found for %s" % self.key)
            return

        for comment in ret['comments']:
            ref_id = comment['id']
            key = '_'.join(['digg', 'comment', ref_id])
            c = models.DiggUserComment.get_or_insert(key_name=key,
                                                     parent=self.epos,
                                                     ref_id=ref_id,
                                                     activity_created=datetime.utcfromtimestamp(comment['date']))
            c.ref_id = ref_id
            c.diggs = comment['up']
            c.buries = comment['down']
            c.body = comment['content']
            c.author = comment['icon']
            #c.relative_rank = 0
            c.put()
            # TODO: need to create relation outside of provider
            #c['reply_to'] = 'digg:%s' % comment['reply_to']
