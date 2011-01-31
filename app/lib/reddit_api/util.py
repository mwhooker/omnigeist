import time
import urlparse

from functools import wraps

def limit_chars(num_chars=80):
    """
    A decorator to limit the number of chars in a function that outputs a
    string.
    """
    def func_limiter(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            if len(value) > num_chars:
                value = value[:num_chars] + "..."
            return value
        return func_wrapper
    return func_limiter

def urljoin(base, subpath, *args, **kwargs):
    """
    Does a urljoin with a base url, always considering the base url to end
    with a directory, and never truncating the base url.
    """
    subpath = subpath.lstrip("/")

    if not subpath:
        return base
    if not base.endswith("/"):
        return urlparse.urljoin(base + "/", subpath, *args, **kwargs)
    return urlparse.urljoin(base, subpath, *args, **kwargs)
