from google.appengine.ext import db
from digg.api import Digg2

from omnigeist.activity import abstract
from omnigeist.model import model

class Digg(abstract.Activity):

    def __init__(self, url):
        super(Digg, self).__init__(self, url)
        self.digg = Digg2()

        info = self.digg.story.getInfo(links=[url])

    def _create_epos(self):
        epos = model.Epos.get_or_insert(self.root_key, host=host,
                                        host_link=db.Link(self.link),
                                        link=db.Link(url))


    @property
    def exists(self):
        pass
