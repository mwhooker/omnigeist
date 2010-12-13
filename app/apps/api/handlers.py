# -*- coding: utf-8 -*-
import logging
import shorturl
from tipfy import RequestHandler, Response, render_json_response
from digg.api import Digg2



class OmniApiHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""

        d = Digg2()
        o = d.comment.getInfo(comment_ids="20100728165300:34051976")
        return Response(o)


class ResolveShortUrlHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""
        r = {'location': shorturl.resolve(self.request.args['url'])}
        logging.debug(r)
        return render_json_response(r)
