"""Tornado handlers for frontend config storage."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from notebook.base.handlers import APIHandler
from tornado import gen, web
import json
import os
from .progress_counter import progress_counter
from .debug_env import *
from .common_builder import CommonBuilder
from .tianchi_user_check import not_tianchi_user
import uuid
from .debug_env import *
from .common_builder import CommonBuilder
from urllib.parse import quote, urlencode
from .cookie_utils import *

class CommunityNotebookUploadBuilder(CommonBuilder):
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

    def get_file_name(self, path):
        end_location = path.rfind('/')
        if end_location >= 0:
            return path[end_location + 1:]
        else:
            return path


class CommunityNotebookUploadHandler(APIHandler):
    def initialize(self, builder):
        self.builder = builder
        self.domain = os.environ['dsw_dswDomain'];
        self.url = 'http://' + self.domain

    @not_tianchi_user
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
        params = {'ticket': uid}
        if 'raceId' in data:
            params['raceId'] = data['raceId']
        if 'dataIds' in data:
            params['dataIds'] = data['dataIds']
        parameters = urlencode(params, safe='/', quote_via=quote)
        url = self.url + '/dev/publishNotebook'
        self.log.warn('url is %s?%s', url, parameters)
        id = str(uuid.uuid1())
        if '/' in data['file']:
            id = id + data['file'].split('/')[-1]
        else:
            id = id + data['file']
        user_cookie = get_specific_cookie(self.cookies)
        self.log.warn('user_cookie is %s', user_cookie)
        progress_counter.upload_async(self.log, id, url, data['file'], parameters, None, cookies = user_cookie)
        self.finish(json.dumps({'id': id}))
        self.set_status(200)


# The path for lab build.
community_upload_notebook_path = r"/lab/api/community/notebook/upload"
