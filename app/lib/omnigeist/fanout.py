import logging

from google.appengine.ext import db

from omnigeist import activity
from omnigeist import models

activity_map = {'digg': 'DiggProvider'}

def fanout(c_url):
    """TODO: we should raise recoverable errors so the taskqueue can retry the fanout"""
    logging.debug("canonicalizing url: %s" % c_url)
    providers = [activity.DiggProvider,
                 activity.RedditProvider]
    for provider in providers:
        try:
            pobj = provider(c_url)
            pobj.update_events(pobj.last_updated)
        except activity.NoActivityException, e:
            logging.debug("no activity for provider %s, url %s" % (
                provider.__class__, c_url))
        except activity.ActivityException, e:
            logging.debug("problem fetching activity for %s. url %s" % (
                provider.__class__.__name__, c_url))
        except Exception, e:
            logging.error("failed updating events for provider %s, url %s."
                          "encountered exception %s: %s" % (
                              provider, c_url, type(e), e))
    """
    for host in activity_map:
        klass = getattr(provider, activity_map[host])
        try:
            activity = klass(c_url)
        except Exception, e:
            logging.debug("couldn't construct klass %s: '%s'" % (klass, e))
            continue

        last_updated = epos.updated_on

        for k in activity.data:
            setattr(epos, k, activity.data[k])

        for event in activity.events(start_date=last_updated):
            event.put()
            ""
            logging.debug("found event %s" % event)
            event_klass = model.activity_factory(event['kind'])
            event_model = event_klass.get_or_insert(event.get_key(), parent=epos, **event)
            for i in event:
                setattr(event_model, i, event[i])
            event_model.put()
            ""
    """
