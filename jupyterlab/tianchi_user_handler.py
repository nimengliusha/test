"""Tornado handlers for frontend config storage."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from notebook.base.handlers import APIHandler
from .common_builder import CommonBuilder
from .tianchi_service import *
from .tianchi_service import tianchi, tianchi_url


class TianchiUserBuilder(CommonBuilder):
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


class TianchiUserHandler(APIHandler):
    def initialize(self, builder):
        self.builder = builder
        self.domain = os.environ['dsw_dswDomain'];
        self.url = 'http://' + self.domain + '/demos'
        self.tianchi_url = 'http://' + self.domain

    @web.authenticated
    @gen.coroutine
    def get(self):
        self.log.warn('enter TianchiUserHandler')
        joined = yield tianchi.is_tianchi_joined(self.log, self.get_cookie('login_aliyunid_ticket'), tianchi_url, cookies=self.cookies)
        if joined:
            self.finish(json.dumps({'joined': True}))
            return
        else:
            self.finish(json.dumps({'joined': False}))


# The path for lab build.
tianchi_user_path = r"/lab/api/tianchi/joined"
