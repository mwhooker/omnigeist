from google.appengine.ext import db
from google.appengine.ext.db import polymodel


class Epos(db.Expando):
    """Root record of activity for a property-url"""

    host = db.StringProperty(required=True, choices=set(['digg', 'twitter', 'reddit']))
    # The resource we're tracking
    url = db.LinkProperty()
    ref_id = db.StringProperty()
    author = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    updated_on = db.DateTimeProperty(auto_now=True)

class UserActivity(polymodel.PolyModel):
    ref_id = db.StringProperty(required=True)
    author = db.StringProperty()
    activity_created = db.DateTimeProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    updated_on = db.DateTimeProperty(auto_now=True)

class UserComment(UserActivity):
    reply_to = db.SelfReferenceProperty()
    body = db.TextProperty()

class DiggUserComment(UserComment):
    # up - down, usually
    diggs = db.IntegerProperty()
    up = db.IntegerProperty()
    down = db.IntegerProperty()

class RedditUserComment(UserComment):
    ups = db.IntegerProperty()
    downs = db.IntegerProperty()
