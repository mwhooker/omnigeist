import logging

from google.appengine.ext import db

from omnigeist.activity import provider
from omnigeist.model import model
from omnigeist import http_util

activity_map = {'digg': 'DiggProvider'}

def fanout(url):
    c_url = http_util.canonicalize_url(url)
    logging.debug("canonicalizing url: %s" % c_url)
    for host in activity_map:
        klass = getattr(provider, activity_map[host])
        try:
            activity = klass(c_url)
        except Exception, e:
            logging.debug("couldn't construct klass %s: '%s'" % (klass, e))
            continue

        epos = model.Epos.get_or_insert(activity.get_key(),
                                        url=db.Link(activity.url),
                                        ref_id=activity.data['ref_id'],
                                        host=host)
        last_updated = epos.updated_on

        for k in activity.data:
            setattr(epos, k, activity.data[k])

        for event in activity.events(start_date=last_updated):
            logging.debug("found event %s" % event)
            event_klass = model.activity_factory(event['kind'])
            event_model = event_klass.get_or_insert(event.get_key(), parent=epos, **event)
            for i in event:
                setattr(event_model, i, event[i])
            event_model.put()
