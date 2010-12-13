import logging

from google.appengine.ext import db
from digg.api import Digg2

from omnigeist.activity import abstract
from omnigeist.model import model

class Digg(abstract.Activity):

    def __init__(self, url):
        super(Digg, self).__init__(url)
        self.data = {}
        self.digg = Digg2()

        link = ",".join([url])
        info = self.digg.story.getInfo(links=link)
        logging.debug(info)

        if info['count'] == 0:
            raise Exception("doesn't exist")

        story = info['stories'][0]
        self.data['ref_id'] = story['story_id']
        self.data['diggs'] =  story['diggs']
        self.data['permalink'] = story['permalink']
        self.url = url

    def _create_epos(self):
        epos = model.Epos.get_or_insert(self.root_key, host='digg',
                                        url=db.Link(self.url),
                                       **self.data)
        logging.debug(epos)


    def write_events(self):
        pass
