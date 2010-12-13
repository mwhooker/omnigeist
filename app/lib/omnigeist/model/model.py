from google.appengine.ext import db
from google.appengine.ext.db import polymodel


class Epos(db.Expando):
    """Root record of activity for a property-url"""

    host = db.StringProperty(required=True, choices=set(['digg', 'twitter']))
    # The resource we're tracking
    url = db.LinkProperty()
    ref_id = db.StringProperty()
    created_on = db.DateProperty(auto_now_add=True)

class UserActivity(polymodel.PolyModel):
    author = db.StringProperty()
    ref_id = db.StringProperty()
    epos = db.ReferenceProperty(Epos)

class UserComment(UserActivity):
    reply_to = db.SelfReferenceProperty()
    body = db.TextProperty()

class DiggUserComment(UserComment):
    diggs = db.IntegerProperty()
    buries = db.IntegerProperty()
