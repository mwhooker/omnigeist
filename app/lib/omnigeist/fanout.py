import logging

from google.appengine.ext import db

from omnigeist.activity import provider
from omnigeist import models
from omnigeist import http_util

activity_map = {'digg': 'DiggProvider'}

def fanout(url):
    c_url = http_util.canonicalize_url(url)
    logging.debug("canonicalizing url: %s" % c_url)
    try:
        digg_provider = provider.DiggProvider(c_url)
        digg_provider.update_events(digg_provider.last_updated)
    except:
        pass
    reddit_provider = provider.RedditProvider(c_url)
    reddit_provider.update_events(reddit_provider.last_updated)
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
