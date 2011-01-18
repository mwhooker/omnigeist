from omnigeist import models

from google.appengine.ext import db


class ActivityException(Exception): pass

class NoActivityException(ActivityException): pass
        

class Activity(object):


    def update_events(self, last_updated):
        raise NotImplementedError
