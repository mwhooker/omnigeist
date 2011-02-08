import httplib2
import urlparse

from google.appengine.api import memcache


class ResolveException(Exception): pass

class MemcacheFileAdapter(httplib2.FileCache):
    def __init__(self, namespace=None, **kwargs):
        self.client = memcache.Client()
        if namespace:
            self.namespace = namespace
        else:
           self.namespace = self.__class__.__name__

    def delete(self, key):
        self.client.delete(key, namespace=self.namespace)

    def get(self, key):
        return self.client.get(key, namespace=self.namespace)

    def set(self, key, value):
        self.client.set(key, value, namespace=self.namespace)

def canonicalize_url(url):
    """Canoninicalize urls. a semantic operation.

    >>> canonicalize_url('hTTP://EN.WIKIPEDIA.ORG:80/wiki/Time_Warner?x=1&y=2#frag')
    'http://en.wikipedia.org/wiki/Time_Warner?x=1&y=2'
    >>> canonicalize_url('http://example.com?a=1&b=2')
    'http://example.com?a=1&b=2'
    >>> canonicalize_url('http://example.com?b=2&a=1')
    'http://example.com?a=1&b=2'
    >>> canonicalize_url('http://localhost:8080')
    'http://localhost:8080'
    >>> canonicalize_url('http://abcnews.go.com/GMA/video/facebook-blues-12796540?')
    'http://abcnews.go.com/GMA/video/facebook-blues-12796540'
    >>> canonicalize_url('http://abcnews.go.com/GMA/video/facebook-blues-12796540')
    'http://abcnews.go.com/GMA/video/facebook-blues-12796540'
    """

    key = '_'.join(['c14n', url])
    cached_url = memcache.get(key)
    if cached_url:
        return cached_url

    #url = resolve_shorturl(url)
    # trim off fragment
    scheme, netloc, path, query, _ = urlparse.urlsplit(url)

    # sort query string
    query = '&'.join(sorted(query.split('&')))

    # lowercase scheme and netloc
    scheme, netloc = map(str.lower, [scheme, netloc])

    #remove default port if exists
    if netloc[-3:] == ':80':
        netloc = netloc[:-3]

    c14n = urlparse.urlunsplit((scheme, netloc, path, query, None))
    memcache.set(key, c14n)
    return c14n


def resolve_shorturl(url):

    h = httplib2.Http(cache=MemcacheFileAdapter('shorturl'))

    try:
        resp, _ = h.request(url, "HEAD", redirections=10)
    except httplib2.HttpLib2Error, e:
        raise ResolveException(e)

    try: 
        # resp['content-location'] doesn't work as detailed here
        # http://code.google.com/p/httplib2/issues/detail?id=19
        if resp.previous is None:
            return url
        else:
            return resp.previous['location']
    except KeyError:
        raise ResolveException()
