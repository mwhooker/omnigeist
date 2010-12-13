import urlparse

#TODO: move to config
activity_map = {'digg': 'omnigeist.activity.digg.Digg'}
map(__import__, activity_map.values())

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
    scheme, netloc = map(str.lower, [scheme, netloc])

    #remove default port if exists
    if netloc[-3:] == ':80':
        netloc = netloc[:-3]

    return urlparse.urlunsplit((scheme, netloc, path, query))

def fanout(url):
    c_url = canonicalize_url(url)
    for host in activity_map:
        klass = __import__(activity_map[host])
        activity = klass(c_url)
        if not klass.exists:
            continue
        activity.write_events()
