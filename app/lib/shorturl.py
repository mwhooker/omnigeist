import httplib2

USER_AGENT = "Python/shorturl.py"
# TODO: find file-like cache in GAE for this
h = httplib2.Http()


class ResolveException(Exception): pass

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
