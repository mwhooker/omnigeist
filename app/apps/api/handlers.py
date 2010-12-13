# -*- coding: utf-8 -*-
import logging
import shorturl
from tipfy import RequestHandler, Response, render_json_response
from omnigeist import activity


class OmniApiHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""
        activity.fanout(self.request.args['url'])
        return Response("OK")


class ResolveShortUrlHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""
        r = {'location': shorturl.resolve(self.request.args['url'])}
        logging.debug(r)
        return render_json_response(r)
