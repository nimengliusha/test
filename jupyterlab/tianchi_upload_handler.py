"""Tornado handlers for frontend config storage."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from concurrent.futures import ThreadPoolExecutor
import json
from threading import Event

from notebook.base.handlers import APIHandler
from tornado import gen, web
from tornado.concurrent import run_on_executor

from jupyterlab.cookie_utils import get_specific_cookie
from jupyterlab.tianchi_user_check import tianchi_user
from .commands import build, clean, build_check
from urllib import request, parse
import json
from pathlib import Path
from .openapi import send_request, get_download_request
import os
from .progress_counter import progress_counter
import uuid
from .debug_env import *
from .common_builder import CommonBuilder
from urllib.parse import quote, urlencode


class TianchiUploadBuilder(CommonBuilder):
    building = False
    executor = ThreadPoolExecutor(max_workers=5)
    canceled = False
    _canceling = False
    _kill_event = None
    _future = None

    def __init__(self, log, core_mode, app_dir):
        super().__init__(log)
        self.log = log
        self.core_mode = core_mode
        self.app_dir = app_dir

    @gen.coroutine
    def get_download_request(self, url, arg):
        key = os.environ['dsw_serviceId'];
        token = os.environ['dsw_token'];
        self.log.warn('token is %s', token)
        self.log.warn('key is %s', key)
        query, headers = get_download_request(self.log, key,
                                              token, url, arg)
        raise gen.Return([url, query, headers]);


class TianchiUploadHandler(APIHandler):
    def initialize(self, builder):
        self.builder = builder
        self.domain = os.environ['dsw_dswDomain'];
        self.url = 'http://' + self.domain

    @tianchi_user
    @web.authenticated
    @gen.coroutine
    def post(self):
        self.log.warn('args is %s', self.get_json_body())
        data = self.get_json_body()
        if "dsw_debug" in os.environ:
            uid = debug_login_aliyunid_ticket
        else:
            uid = self.get_cookie('login_aliyunid_ticket');
        self.log.warn('uid is %s', uid)
        parameters = urlencode({'ticket': uid, 'name': data['game']}, safe='/', quote_via=quote)
        url = self.url + '/api/data/submit'
        self.log.warn('url is %s?%s', url, parameters)
        id = str(uuid.uuid1())
        if '/' in data['name']:
            id = id + data['name'].split('/')[-1]
        else:
            id = id + data['name']
        user_cookie = get_specific_cookie(self.cookies)
        progress_counter.upload_async(self.log, id, url, data['name'], parameters, None, cookies = user_cookie)
        self.finish(json.dumps({'id': id}))
        self.set_status(200)


# The path for lab build.
tianchi_upload_path = r"/lab/api/tianchi/upload"
