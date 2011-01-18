from omnigeist import models

from google.appengine.ext import db


class ActivityException(Exception): pass

class NoActivityException(ActivityException): pass
        

class Activity(object):


    def update_events(self, last_updated):
        raise NotImplementedError

    @property
    def last_updated(self):
        return self.epos.updated_on

    @staticmethod
    def _get_or_create_epos(url, host):
        # TODO: validate that host exists
        key = '_'.join(['epos', host, url])
        epos = models.Epos.get_or_insert(key_name=key,
                                         url=db.Link(url),
                                         host=host)
        return epos
