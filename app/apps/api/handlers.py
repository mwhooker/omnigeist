# -*- coding: utf-8 -*-
import logging
import simplejson as json

from tipfy import RequestHandler, Response, render_json_response

from omnigeist import fanout
from omnigeist import http_util
from omnigeist import models


class MainApiHandler(RequestHandler):
    def get(self):
        logging.debug("fanout")
        fanout.fanout(self.request.args['url'])
        return Response("OK")


class TopApiHandler(RequestHandler):
    def get(self, format):
        providers = ('digg', 'reddit')
        if self.request.args.get('provider') not in providers\
           or 'url' not in self.request.args:
            return Response(status=400)

        provider = self.request.args['provider']
        url = http_util.canonicalize_url(self.request.args['url'])
        idx = int(self.request.args.get('idx', 1))
        if idx < 1:
            idx = 1
        
        resp = {}
        if provider == 'digg':
            top = models._get_top_digg_comment(url, idx)
            if not top:
                return Response(status=404)
            resp['diggs'] = top.diggs
            resp['up'] = top.up
            resp['buries'] = top.down
        elif provider == 'reddit':
            top = models._get_top_reddit_comment(url, idx)
            if not top:
                return Response(status=404)
            resp['ups'] = top.ups
            resp['down'] = top.downs

        for attr in ('author', 'created_on', 'body'):
            resp[attr] = str(top.__getattribute__(attr))

        if format == 'js':
            callback = self.request.args.get('callback')
            if not callback:
                return Response(status=401)
            response = Response("%s(%s);" % ( callback, json.dumps(resp)))
            response.headers['Content-Type'] = 'text/javascript'
            return response
        elif format == 'json':
            return render_json_response(resp)


class ResolveShortUrlHandler(RequestHandler):
    def get(self):
        """Simply returns a Response object with an enigmatic salutation."""
        r = {'location': http_util.resolve_shorturl(self.request.args['url'])}
        logging.debug(r)
        return render_json_response(r)
