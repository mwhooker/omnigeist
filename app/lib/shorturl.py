import httplib2
from google.appengine.api import memcache

USER_AGENT = "Python/shorturl.py"
# TODO: find file-like cache in GAE for this

class ResolveException(Exception): pass

class MemcacheAdapter(httplib2.FileCache):
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

h = httplib2.Http(MemcacheAdapter('shorturl'))

def resolve(url):

    headers = { 'User-Agent' : USER_AGENT }

    try:
        resp, _ = h.request(url, "HEAD")
    except httplib2.HttpLib2Error, e:
        raise ResolveException(e)

    try: 
        # resp['content-location'] doesn't work as detailed here
        # http://code.google.com/p/httplib2/issues/detail?id=19
        return resp.previous['location']
    except KeyError:
        raise ResolveException()
