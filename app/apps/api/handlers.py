# -*- coding: utf-8 -*-
import logging

from tipfy import RequestHandler, Response, render_json_response

from omnigeist import fanout
from omnigeist import http_util


class OmniApiHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""
        logging.debug("fanout")
        fanout.fanout(self.request.args['url'])
        return Response("OK")


class ResolveShortUrlHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""
        r = {'location': http_util.resolve_shorturl(self.request.args['url'])}
        logging.debug(r)
        return render_json_response(r)
