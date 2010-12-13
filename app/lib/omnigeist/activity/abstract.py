from omnigeist.model import model
        

class Activity(object):


    def __init__(self, url):
        self.url = url

    def _create_epos(self):
        raise NotImplementedError

    def write_events(self):
        raise NotImplementedError

    @property
    def root_key(self):
        key = '_'.join([self.__class__.__name__, self.url])
