import urlparse
from omnigeist.activity import provider

activity_map = {'digg': 'Digg'}

def canonicalize_url(url):
    """Canoninicalize urls

    >>> canonicalize_url('hTTP://EN.WIKIPEDIA.ORG:80/wiki/Time_Warner?x=1&y=2#frag')
    http://en.wikipedia.org/wiki/Time_Warner?x=1&y=2
    >>> canonicalize_url('http://localhost:8080')
    http://localhost:8080
    """

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
    for host in activity_map:
        #klass = __import__(activity_map[host], globals(), locals())
        klass = getattr(provider, activity_map[host])
        try:
            activity = klass(c_url)
        except:
            continue
        activity.write_events()
