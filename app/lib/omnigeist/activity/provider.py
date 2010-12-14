import logging

from digg.api import Digg2

from omnigeist.activity import abstract

class Digg(abstract.Activity):

    def __init__(self, url):
        super(Digg, self).__init__(url)
        self.data = {}
        self.digg = Digg2()

        link = ",".join([url])
        info = self.digg.story.getInfo(links=link)
        logging.debug(info)

        if info['count'] == 0:
            raise abstract.NoActivityException()

        story = info['stories'][0]
        self.data['ref_id'] = story['story_id']
        self.data['diggs'] =  story['diggs']
        self.data['permalink'] = story['permalink']


    def events(self, start_date):

        c = CommentEvent('kind')
        c['diggs'] = 4
        c['buries'] = 1
        c['body'] = 'test'
        c['author'] = 'matt'
        c['ref_id'] = '1243'
        yield c

class CommentEvent(abstract.Event):

    def get_key(self):
        return self['ref_id']
