# -*- coding: utf-8 -*-
import logging

from tipfy import RequestHandler, get_config
from tipfy.ext.jinja2 import render_template, render_response, get_jinja2_instance
from jinja2 import MemcachedBytecodeCache
from google.appengine.api.memcache import Client as MemcachedClient

if get_config('web', 'jinja.caching', False):
    env = get_jinja2_instance()
    logging.debug("setting up mcd client")
    env.bytecode_cache = MemcachedBytecodeCache(MemcachedClient())

class BookmarkletWebHandler(RequestHandler):
    def get(self):
        return render_response('bookmarklet.js',
                               host=get_config('web', 'host'))

class ClientWebHandler(RequestHandler):
    def get(self):
        c = {'host': get_config('web', 'host')}
        return render_response('omnigeist/client.js',
                               comment_tpl=self.render_js_template('omnigeist/comment_tpl.html', **c),
                               client_tpl=self.render_js_template('omnigeist/client_tpl.html', **c))

    def render_js_template(self, template, **kwargs):
        return ' '.join(render_template(template, **kwargs).splitlines())
