"""Tornado handlers for frontend config storage."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from .env import WHITE_LIST_PATH
from notebook.base.handlers import APIHandler
from tornado import gen, web
import json
from .common_builder import CommonBuilder
from .openapi import *
import os

class NotebookProxyBuilder(CommonBuilder):

    def __init__(self, log, core_mode, app_dir):
        super().__init__(log)
        self.log = log
        self.core_mode = core_mode
        self.app_dir = app_dir


class NotebookProxyHandler(APIHandler):
    def initialize(self, builder):
        self.builder = builder
        self.domain = os.environ['dsw_dswDomain'];
        self.url = 'http://' + self.domain + '/'

    @web.authenticated
    @gen.coroutine
    def get(self, path):
        if path not in WHITE_LIST_PATH:
            self.finish(json.dumps({'success': False, 'error': 'path is not in whitelist'}))
            return;
        query_arguments = self.request.query_arguments
        body_arguments = self.request.body_arguments
        cookies = self.request.cookies
        headers = self.request.headers
        method = self.request.method
        self.log.info(
            "path is %s, query_arguments is %s, body_arguments is %s, headers is %s, method is %s ",
            path, query_arguments, body_arguments, headers, method)
        try:
            res = forward_request_without_auth(self.log, self.url + path, query_arguments, body_arguments, headers,
                                               cookies, method)
            self.finish(json.dumps({'success': True, 'data': res}))
        except Exception as inst:
            self.log.error(u'Error while send request: %s', inst, exc_info=True)
            self.finish(json.dumps({'success': False, 'error': str(inst)}))

    @web.authenticated
    @gen.coroutine
    def post(self, path):
        if path not in WHITE_LIST_PATH:
            self.finish(json.dumps({'success': False, 'error': 'path is not in whitelist'}))
            return;
        query_arguments = self.request.query_arguments
        body_arguments = self.request.body
        cookies = self.request.cookies
        headers = self.request.headers
        method = self.request.method
        self.log.info(
            "path is %s, query_arguments is %s, body_arguments is %s, headers is %s, method is %s ",
            path, query_arguments, body_arguments, headers, method)
        try:
            res = forward_request_without_auth(self.log, self.url + path, query_arguments, body_arguments, headers,
                                               cookies, method)
            self.finish(json.dumps({'success': True, 'data': res}))
        except Exception as inst:
            self.log.error(u'Error while send request: %s', inst, exc_info=True)
            self.finish(json.dumps({'success': False, 'error': str(inst)}))

    @web.authenticated
    @gen.coroutine
    def post(self, path):
        if path not in WHITE_LIST_PATH:
            self.finish(json.dumps({'success': False, 'error': 'path is not in whitelist'}))
            return;
        query_arguments = self.request.query_arguments
        body_arguments = self.request.body
        cookies = self.request.cookies
        headers = self.request.headers
        method = self.request.method
        self.log.info(
            "path is %s, query_arguments is %s, body_arguments is %s, cookies is %s,headers is %s, method is %s ",
            path, query_arguments, body_arguments, cookies, headers, method)
        try:
            res = forward_request_without_auth(self.log, self.url + path, query_arguments, body_arguments, headers,
                                               cookies, method)
            self.finish(json.dumps({'success': True, 'data': res}))
        except Exception as inst:
            self.log.error(u'Error while send request: %s', inst, exc_info=True)
            self.finish(json.dumps({'success': False, 'error': str(inst)}))


notebook_proxy_path = r"/lab/api/notebook/proxy/(.*)"
