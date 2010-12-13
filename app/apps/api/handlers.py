# -*- coding: utf-8 -*-
from tipfy import RequestHandler, Response


class OmniApiHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""
        return Response('Hello, World!')
