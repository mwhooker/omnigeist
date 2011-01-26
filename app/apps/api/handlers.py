# -*- coding: utf-8 -*-
import logging
import time
import hashlib
import simplejson as json

from google.appengine.api import memcache
from google.appengine.api import taskqueue

from tipfy import RequestHandler, Response, render_json_response

from omnigeist import fanout
from omnigeist import http_util
from omnigeist import models


class FanoutApiHandler(RequestHandler):
    def get(self):
        url = self.request.args.get('url')
        if not url:
            self.abort(400)
        c_url = http_util.canonicalize_url(url)
        fanout.fanout(c_url)
        return Response()

    def post(self):
        logging.debug("fanout")
        url = self.request.form.get('url')
        if not url:
            self.abort(400)
        c_url = http_util.canonicalize_url(url)

        fanout.fanout(c_url)

        return Response()


class TopApiHandler(RequestHandler):

    def get(self, format):
        providers = ('digg', 'reddit')
        if self.request.args.get('provider') not in providers\
           or 'url' not in self.request.args:
            self.abort(400)

        provider = self.request.args['provider']
        url = http_util.canonicalize_url(self.request.args['url'])

        try:
            idx = int(self.request.args.get('idx', 1))
        except ValueError:
            self.abort(400)
        if idx < 1:
            idx = 1
        
        mcd = memcache.Client()

        def _load_top():
            resp_cache_key = '_'.join(['cache_top', url])
            resp = mcd.get(resp_cache_key)
            resp = {}
            if provider == 'digg':
                top = models._get_top_digg_comment(url, idx)
                if top:
                    resp['diggs'] = top.diggs
                    resp['up'] = top.up
                    resp['buries'] = top.down
            elif provider == 'reddit':
                top = models._get_top_reddit_comment(url, idx)
                if top:
                    resp['ups'] = top.ups
                    resp['down'] = top.downs

            if top:
                for attr in ('author', 'created_on', 'body'):
                    resp[attr] = str(top.__getattribute__(attr))

            if len(resp):
                mcd.set(resp_cache_key, resp, 60*15)
                return resp
            else:
                return False

        # check data for freshness
        freshness_key = '_'.join(['url_fresh', url])
        if mcd.add(freshness_key, True, 60*60):
            # add to task queue. immediately continue
            r = taskqueue.add(url='/fanout', name=hashlib.md5(url).hexdigest(),
                          queue_name='fanout-queue', params={'url': url})

        resp = _load_top()
        # No data from the db
        if not resp:
            # do the fanout in-band and return the result
            try:
                fanout.fanout()
            except:
                self.abort(500)
            resp = _load_top()
            if not resp:
                self.abort(404)

        if format == 'js':
            callback = self.request.args.get('callback')
            if not callback:
                self.abort(401)
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
