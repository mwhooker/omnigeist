# -*- coding: utf-8 -*-
import logging
import time
import math
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
        if 'url' not in self.request.args:
            self.abort(400)

        url = http_util.canonicalize_url(self.request.args['url'])

        try:
            idx = int(self.request.args.get('idx', 1))
        except ValueError:
            self.abort(400)
        if idx < 1:
            idx = 1
        

        def _load_top():
            resp_cache_key = '_'.join(['cache_top', url])
            resp = memcache.get(resp_cache_key)
            if resp:
                return resp
            else:
                resp = {}

            top = models._get_top_digg_comment(url, idx)
            if top:
                diggs = []
                for i in top:
                    digg = {}
                    digg['diggs'] = i.diggs
                    digg['up'] = i.up
                    digg['buries'] = i.down
                    for attr in ('author', 'created_on', 'body'):
                        digg[attr] = unicode(i.__getattribute__(attr))
                    diggs.append(digg)
                resp['digg'] = diggs
            top = models._get_top_reddit_comment(url, idx)
            if top:
                reddits = []
                for i in top:
                    reddit = {}
                    reddit['ups'] = i.ups
                    reddit['down'] = i.downs
                    for attr in ('author', 'created_on', 'body'):
                        reddit[attr] = unicode(i.__getattribute__(attr))
                    reddits.append(reddit)
                resp['reddit'] = reddits

            if len(resp):
                memcache.set(resp_cache_key, resp, 60*15)
                return resp
            else:
                return False

        # TODO: would like to not be calling fanout as often.
        #       fanout happens twice on a new url. once in queue, one in-band
        # check data for freshness
        freshness_key = '_'.join(['url_fresh', url])
        if memcache.add(freshness_key, True, 60*60):
            # add to task queue. immediately continue
            """prefix key with hours since epoch to circumvent issues in
            http://code.google.com/p/googleappengine/issues/detail?id=2459"""
            name = "%s-%s" % (int(math.floor(time.time() / 60)),
                              hashlib.md5(url).hexdigest())
            r = taskqueue.add(url='/fanout', name=name,
                          queue_name='fanout-queue', params={'url': url})

        resp = _load_top()
        # No data from the db
        if not resp:
            # do the fanout in-band and return the result
            try:
                fanout.fanout(url)
            except Exception, e:
                logging.error(e)
                self.abort(500)
            resp = _load_top()
            if not resp:
                logging.info("no activity found for %s" % url)
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
