"""Tornado handlers for frontend config storage."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from concurrent.futures import ThreadPoolExecutor

from notebook.base.handlers import APIHandler
from tornado import gen, web
import json
import os
from .progress_counter import progress_counter
from .debug_env import *
from .common_builder import CommonBuilder
from .tianchi_user_check import not_tianchi_user
from .env import HOME_DIR
import uuid

class CommunityNotebookDownloadBuilder(CommonBuilder):
    building = False
    canceled = False
    _canceling = False
    _kill_event = None
    _future = None

    def __init__(self, log, core_mode, app_dir):
        super().__init__(log)
        self.log = log
        self.core_mode = core_mode
        self.app_dir = app_dir


class CommunityNotebookDownloadHandler(APIHandler):
    def initialize(self, builder):
        self.builder = builder
        self.domain = os.environ['dsw_dswDomain'];
        self.url = 'http://' + self.domain

    @not_tianchi_user
    @web.authenticated
    @gen.coroutine
    def post(self):
        self.log.warn('enter download, args is %s', self.get_json_body())
        data = self.get_json_body()
        if "dsw_debug" in os.environ:
            uid = debug_login_aliyunid_ticket
        else:
            uid = self.get_cookie('login_aliyunid_ticket')
        self.log.warn('uid is %s', uid)
        url = self.url + '/dev/downloadNotebook/stream?ticket=' + uid + '&labId=' + data['labId'] + '&labVersion=' + \
              data['labVersion']
        if 'forkUserId' in data:
            url = url + '&forkUserId=' + data['forkUserId']
        self.log.warn('url is %s', url)
        unique_id = str(uuid.uuid1())
        progress_counter.download_async(id=unique_id, log=self.log, prefix='/' + data['folder'], url=url, file_name=data['name'],
                                        need_decompress=False)
        self.finish(json.dumps({'id': unique_id}))
        self.set_status(200)


community_notebook_download_path = r"/lab/api/community/notebook/download"
