import logging
import httplib2
import urllib
from datetime import datetime

try:
    import simplejson as json
except ImportError:
    import json

import reddit_api as reddit
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
        self.url = c_url
        self.eposi = {}
        h = httplib2.Http(cache=MemcacheFileAdapter('shorturl'))
        self.r = reddit.Reddit(h)
        self.subreddits = None

        try:
            info = self.r.info(c_url)
        except reddit.APIException, e:
            raise ActivityException(e)

        self.subreddits = info
        for subr in self.subreddits:
            subr = subr.__dict__
            epos = self._get_or_create_epos(c_url, str(subr['subreddit']))
            epos.subreddit = str(subr['subreddit'])
            epos.permalink = "%s%s" % (self.REDDIT_URL, subr['permalink'])
            epos.title = subr['title']
            epos.ups = subr['ups']
            epos.downs = subr['downs']
            epos.ref_id = subr['id']
            epos.submitted_on = datetime.utcfromtimestamp(subr['created_utc'])
            epos.author = str(subr['author'])
            epos.put()
            self.eposi[str(subr['subreddit'])] = epos


        # http://www.reddit.com/api/info.json?count=1&url=http://voices.washingtonpost.com/blog-post/2010/12/openleaks_launches_rivals_wiki.html

    def update_events(self, start_date):
        """

        TODO:
            only update events since start_date.
            resolve (in|ex)clusive ambiguity in name
        """

        for subr in self.subreddits:
            comments = subr.get_top(10)
            
            for comment in comments: 
                node = comment.__dict__
                created_on = datetime.utcfromtimestamp(node['created_utc'])
                key = '_'.join(['reddit', 'comment', node['id']])
                c = models.RedditUserComment.get_or_insert(key_name=key,
                                                           parent=self.eposi[subr.subreddit],
                                                           ref_id=node['id'],
                                                           url=self.url,
                                                           activity_created=created_on)
                parent_key = '_'.join(['reddit', 'comment', node['parent_id'].split('_')[1]])
                c.rank = int(node['ups']) - int(node['downs'])
                c.ups = node['ups']
                c.downs = node['downs']
                if node['parent_id'] != node['link_id']:
                    c.reply_to = db.Key.from_path(models.RedditUserComment.kind(),
                                                  parent_key,
                                                  parent=self.eposi[subr.subreddit].key())
                # TODO: make sure this is unicode
                c.body = node['body']
                c.author = str(node['author'])
                c.put()

    @property
    def last_updated(self):
        if not len(self.eposi):
            return None
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
        self.url = c_url
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

        count = ret['count']
        logging.debug("found %d comments" % count)
        if count == 0:
            logging.debug("no comments found for %s" % self.key)
            return

        for comment in ret['comments']:
            ref_id = comment['comment_id']
            key = '_'.join(['digg', 'comment', ref_id])
            c = models.DiggUserComment.\
                    get_or_insert(key_name=key,
                                  parent=self.epos,
                                  ref_id=ref_id,
                                  url=self.url,
                                  activity_created=datetime.utcfromtimestamp(
                                      comment['date_created']))
            c.ref_id = ref_id
            c.up = comment['up']
            c.down = comment['down']
            c.diggs = comment['diggs']
            c.rank = int(comment['diggs'])
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
