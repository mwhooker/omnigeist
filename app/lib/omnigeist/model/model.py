from google.appengine.ext import db
from google.appengine.ext.db import polymodel


class UserActivity(polymodel.PolyModel):
    author = StringType()
    ref_id = db.StringType()
    epos = db.ReferenceProperty(Epos)

class UserComment(UserActivity):
    reply_to = db.SelfReferenceProperty()
    body = db.TextProperty()

class DiggUserComment(UserComment):
    diggs = db.IntegerProperty()
    buries = db.IntegerProperty()

class Epos(db.Expando):
    """Root record of activity for a property-url"""

    host = db.StringType(required=True, choices=set(['digg', 'twitter']))
    #host_link = db.LinkProperty()
    link = db.LinkProperty()
    created_on = db.DateProperty(auto_now_add=True)
