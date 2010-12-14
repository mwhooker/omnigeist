import logging
import httplib2
from datetime import datetime

from digg.api import Digg, Digg2

from omnigeist.activity import abstract
from omnigeist.http_util import MemcacheFileAdapter

class RedditProvider(abstract.Activity):

    def __init__(self, url):
        super(RedditProvider, self).__init__(url)
        self.h = httplib2.Http(cache=MemcacheFileAdapter('shorturl'))

    def events(self, start_date):
        pass

class DiggProvider(abstract.Activity):

    def __init__(self, url):
        super(DiggProvider, self).__init__(url)
        self.data = {}
        digg = Digg2()

        link = ",".join([url])
        info = digg.story.getInfo(links=link)
        logging.debug(info)

        if info['count'] == 0:
            raise abstract.NoActivityException()

        story = info['stories'][0]
        self.story_id = self.data['ref_id'] = story['story_id']
        self.data['diggs'] =  story['diggs']
        self.data['permalink'] = story['permalink']


    def events(self, start_date):
        #TODO: Digg2 api broken for comments
        digg = Digg()
        ret = digg.story.getComments(story_id=self.story_id)

        count = ret['total']
        logging.debug("found %d comments" % count)
        if count == 0:
            logging.debug("no comments found for %s" % self.key)
            return

        for comment in ret['comments']:
            c = CommentEvent('comment')
            c['diggs'] = comment['up']
            c['buries'] = comment['down']
            c['body'] = comment['content']
            c['author'] = comment['icon']
            c['ref_id'] = comment['id']
            c['activity_created'] = datetime.utcfromtimestamp(comment['date'])
            # TODO: need to create relation outside of provider
            #c['reply_to'] = 'digg:%s' % comment['reply_to']
            yield c

class CommentEvent(abstract.Event):

    def get_key(self):
        return ':'.join(['digg', self['ref_id']])
