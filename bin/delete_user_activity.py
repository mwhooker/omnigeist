from google.appengine.ext import db


try:
    while True:
        q = db.GqlQuery("SELECT __key__ FROM UserActivity")
        assert q.count()
        db.delete(q.fetch(200))
        time.sleep(0.5)
except Exception, e:
    pass
