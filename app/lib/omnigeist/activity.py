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

from omnigeist import models
from omnigeist.http_util import MemcacheFileAdapter


class Activity(object):

    def update_events(self, last_updated):
        raise NotImplementedError


class ActivityException(Exception): pass


class NoActivityException(ActivityException): pass

        
class RedditProvider(Activity):
    REDDIT_URL = 'http://www.reddit.com'

    """
    TODO:
        How to model subreddits? for now don't worry about it. understand how we
        want to use the data, first.

        Need to lookup response structure to understand how to store it.
    """

    def __init__(self, c_url):
        self.eposi = {}
        self.h = httplib2.Http(cache=MemcacheFileAdapter('shorturl'))

        info_url = '%s/api/info.json?%s' % (self.REDDIT_URL, 
                                            urllib.urlencode({'count': '1',
                                                              'url': c_url}))
        resp, content = self.h.request(info_url)
        if resp.status > 299:
            raise Exception("error fetching %s" % info_url)
        content = json.loads(content)

        for subr in content['data']['children']:
            epos = self._get_or_create_epos(c_url, subr['data']['subreddit'])
            epos.subreddit = subr['data']['subreddit']
            epos.permalink = "%s%s" % (self.REDDIT_URL, subr['data']['permalink'])
            epos.title = subr['data']['title']
            epos.ups = subr['data']['ups']
            epos.downs = subr['data']['downs']
            epos.ref_id = subr['data']['id']
            epos.submitted_on = datetime.utcfromtimestamp(subr['data']['created_utc'])
            epos.author = subr['data']['author']
            epos.put()
            self.eposi[subr['data']['subreddit']] = epos


        # http://www.reddit.com/api/info.json?count=1&url=http://voices.washingtonpost.com/blog-post/2010/12/openleaks_launches_rivals_wiki.html

    def update_events(self, start_date):
        """

        TODO:
            only update events since start_date.
            resolve (in|ex)clusive ambiguity in name
        """

        for epos in self.eposi:
            info_url = "%s.json" % self.eposi[epos].permalink[:-1]
            resp, content = self.h.request(info_url)

            try:
                content = json.loads(content)
            except json.JSONDecodeError, e:
                logging.debug("error loading %s -> %s" % (info_url, content))
                continue
            logging.info("loading comments from %s" % self.eposi[epos].permalink)

            def _process_node(node):
                created_on = datetime.utcfromtimestamp(node['created_utc'])
                key = '_'.join(['reddit', 'comment', node['id']])
                c = models.RedditUserComment.get_or_insert(key_name=key,
                                                           parent=self.eposi[epos],
                                                           ref_id=node['id'],
                                                           activity_created=created_on)
                parent_key = '_'.join(['reddit', 'comment', node['parent_id'].split('_')[1]])
                c.ups = node['ups']
                c.downs = node['downs']
                if node['parent_id'] != node['link_id']:
                    c.reply_to = db.Key.from_path(models.RedditUserComment.kind(),
                                                  parent_key,
                                                  parent=self.eposi[epos].key())
                    c.body = node['body']
                    c.author = node['author']
                    c.put()

            def _load_activity(children):
                if children['kind'] == 'Listing':
                    for child in children['data']['children']:
                        _load_activity(child)
                elif children['kind'] == 't1':
                    _process_node(children['data'])
                    if len(children['data']['replies']):
                        _load_activity(children['data']['replies'])

            _load_activity(content[1])

    @property
    def last_updated(self):
        return max(self.eposi, key=lambda x: self.eposi[x].updated_on)

    def _get_or_create_epos(self, target_url, subreddit):
        key = '_'.join(['reddit', target_url, subreddit])
        epos = models.Epos.get_or_insert(key_name=key,
                                         url=db.Link(target_url),
                                         host='reddit')
        return epos


class DiggProvider(Activity):
    host = 'digg'


    def __init__(self, c_url):
        self.epos = self._get_or_create_epos(c_url)
        digg_handle = Digg2()

        link = ",".join([self.epos.url])
        info = digg_handle.story.getInfo(links=link)

        if info['count'] == 0:
            raise NoActivityException()

        story = info['stories'][0]
        self.story_id = self.epos.ref_id = story['story_id']
        self.epos.diggs = story['diggs']
        self.epos.permalink = story['permalink']
        self.epos.put()


    def update_events(self, start_date):
        #TODO: Digg2 api broken for comments
        digg_handle = Digg2()
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
            c.up = comment['up']
            c.down = comment['down']
            c.diggs = comment['diggs']
            c.body = comment['text']
            c.author = comment['user']['username']
            if comment['parent_id']:
                parent_key = '_'.join(['digg', 'comment', comment['parent_id']])
                c.reply_to = db.Key.from_path(models.DiggUserComment.kind(),
                                              parent_key,
                                              parent=self.epos.key())


            c.put()

    def _get_or_create_epos(self, target_url):
        # TODO: validate that host exists
        key = '_'.join(['digg', target_url])
        epos = models.Epos.get_or_insert(key_name=key,
                                         url=db.Link(target_url),
                                         host='digg')
        return epos

    @property
    def last_updated(self):
        return self.epos.updated_on
