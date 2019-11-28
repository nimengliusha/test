"""Tornado handlers for frontend config storage."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from concurrent.futures import ThreadPoolExecutor
import json
from threading import Event

from notebook.base.handlers import APIHandler
from tornado import gen, web
from tornado.concurrent import run_on_executor

from jupyterlab.tianchi_user_check import tianchi_user
from .commands import build, clean, build_check
from urllib import request, parse
import json
from pathlib import Path
from .openapi import send_request
import os
from .common_builder import CommonBuilder
from .debug_env import *


class TianchiGameListBuilder(CommonBuilder):
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



class TianchiGameListHandler(APIHandler):
    def initialize(self, builder):
        self.builder = builder
        self.domain = os.environ['dsw_dswDomain'];
        self.url = 'http://' + self.domain

    @tianchi_user
    @web.authenticated
    @gen.coroutine
    def get(self):
        self.log.warn('enter TianchiGameListHandler')
        if "dsw_debug" in os.environ:
            ticket = debug_login_aliyunid_ticket
            user_number = '1586990949331376'
        else:
            ticket = self.get_cookie('login_aliyunid_ticket');
            user_number = os.environ['dsw_userNumber'];
        self.log.warn('uid is %s, ticket is %s', user_number, ticket)
        data = yield self.builder.send_request(self.url + '/games/player/joined', user_number, ticket, None, cookies=self.cookies)
        self.log.warn('data is %s', data)
        files = json.loads(data)
        self.log.warn('files is %s', files)
        if not files['data']:
            self.finish(json.dumps({}))
            return
        self.finish(json.dumps(files['data']))


# The path for lab build.
tianchi_game_list_path = r"/lab/api/tianchi/game/list"
