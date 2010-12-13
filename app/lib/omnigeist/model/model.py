from google.appengine.ext import db



class UserActivity(db.polymodel.PolyModel):
    author = AuthorProperty()
    epos = db.ReferenceProperty(Epos)

class UserComment(UserActivity):
    reply_to = db.SelfReferenceProperty()
    body = db.TextPropert()

class DiggUserComment(UserComment):
    diggs = db.IntegerProperty()
    buries = db.IntegerProperty()

class Epos(db.polymodel.PolyModel):
    """Base class for a record of chatter on a specific property about a spefic
    URL"""

    host = db.StringType(required=True, choices=set(['digg', 'twitter']))
    host_link = db.LinkProperty()
    created_on = db.DateProperty()
