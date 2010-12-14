import urlparse
import logging

import shorturl
from google.appengine.ext import db

from omnigeist.activity import provider
from omnigeist.model import model

activity_map = {'digg': 'DiggProvider'}

def canonicalize_url(url):
    """Canoninicalize urls

    >>> canonicalize_url('hTTP://EN.WIKIPEDIA.ORG:80/wiki/Time_Warner?x=1&y=2#frag')
    http://en.wikipedia.org/wiki/Time_Warner?x=1&y=2
    >>> canonicalize_url('http://localhost:8080')
    http://localhost:8080
    """

    url = shorturl.resolve(url)
    # trim off fragment
    scheme, netloc, path, query, _ = urlparse.urlsplit(url)

    # lowercase scheme and netloc
    scheme, netloc = map(unicode.lower, [scheme, netloc])

    #remove default port if exists
    if netloc[-3:] == ':80':
        netloc = netloc[:-3]

    return urlparse.urlunsplit((scheme, netloc, path, query, None))

def fanout(url):
    c_url = canonicalize_url(url)
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
