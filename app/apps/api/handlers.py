# -*- coding: utf-8 -*-
import logging
import shorturl
from tipfy import RequestHandler, Response, render_json_response
from digg.api import Digg2



class OmniApiHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""

        return Response(o)


class ResolveShortUrlHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""
        r = {'location': shorturl.resolve(self.request.args['url'])}
        logging.debug(r)
        return render_json_response(r)
