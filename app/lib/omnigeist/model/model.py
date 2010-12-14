from google.appengine.ext import db
from google.appengine.ext.db import polymodel


class Epos(db.Expando):
    """Root record of activity for a property-url"""

    host = db.StringProperty(required=True, choices=set(['digg', 'twitter']))
    # The resource we're tracking
    url = db.LinkProperty()
    ref_id = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    updated_on = db.DateTimeProperty(auto_now=True)

class UserActivity(polymodel.PolyModel):
    author = db.StringProperty(required=True)
    ref_id = db.StringProperty(required=True)
    epos = db.ReferenceProperty(Epos)

class UserComment(UserActivity):
    reply_to = db.SelfReferenceProperty()
    body = db.TextProperty()

class DiggUserComment(UserComment):
    diggs = db.IntegerProperty()
    buries = db.IntegerProperty()


def activity_factory(event_kind):
    return DiggUserComment


"""
def activity_from_event(event):
    if not isinstance(event, activity.Event):
        raise ValueError('event must be of type activity.Event')
    model_klass = activity_factory(event.kind)
"""
