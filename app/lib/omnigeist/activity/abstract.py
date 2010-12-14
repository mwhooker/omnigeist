from omnigeist.model import model


class ActivityException(Exception): pass

class NoActivityException(ActivityException): pass
        

class Activity(object):


    def __init__(self, url):
        self.url = url

    def _create_epos(self):
        raise NotImplementedError

    def write_events(self):
        raise NotImplementedError

    def get_key(self):
        return '_'.join([self.__class__.__name__, self.url])


class Event(dict):

    def __init__(self, kind):
        self['kind'] = kind

    @property
    def model(self):
        raise NotImplementedError

    def get_key(self):
        raise NotImplementedError
