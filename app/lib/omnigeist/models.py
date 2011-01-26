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
    url = db.LinkProperty()
    ref_id = db.StringProperty(required=True)
    author = db.StringProperty()
    activity_created = db.DateTimeProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    updated_on = db.DateTimeProperty(auto_now=True)

class UserComment(UserActivity):
    rank = db.IntegerProperty()
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

#activity per page
APP = 20

def _get_top_reddit_comment(url, idx=1):
    query = RedditUserComment.gql("WHERE url = :url AND reply_to = NULL ORDER BY rank DESC",
                                  url=url)
    res = query.fetch(APP, APP*(idx-1))
    if not len(res):
        return None
    return res

def _get_top_digg_comment(url, idx=1):
    query = DiggUserComment.gql("WHERE url = :url AND reply_to = NULL ORDER BY rank DESC",
                                url=url)
    res = query.fetch(APP, APP*(idx-1))
    if not len(res):
        return None
    return res
