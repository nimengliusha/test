"""Tornado handlers for frontend config storage."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from concurrent.futures import ThreadPoolExecutor
import json
from threading import Event

from notebook.base.handlers import APIHandler

from jupyterlab.cookie_utils import get_specific_cookie
from jupyterlab.tianchi_user_check import not_tianchi_user
from .progress_counter import progress_counter
import uuid
from .common_builder import CommonBuilder
from .tianchi_service import *
from urllib.parse import quote, urlencode
from .tianchi_service import tianchi, tianchi_url
from .env import *


class DemoBuilder(CommonBuilder):
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


class DemoHandler(APIHandler):
    def initialize(self, builder):
        self.log.warn('init DemoHandler')
        self.builder = builder
        self.domain = os.environ['dsw_dswDomain'];
        self.url = 'http://' + self.domain + '/demos'
        self.tianchi_url = 'http://' + self.domain
        self.type_by_id = {}
        self.type_by_id[1] = '/Demo/Cases'
        self.type_by_id[2] = '/Demo/DataSets'
        self.type_by_id[3] = '/Demo/Models'
        for key, value in self.type_by_id.items():
            dir = HOME_DIR + value
            if not os.path.exists(dir):
                os.makedirs(dir)
        if "dsw_debug" in os.environ:
            if not os.path.exists(os.environ['dsw_test_folder'] + '/Demo'):
                os.makedirs(os.environ['dsw_test_folder'] + '/Demo')
        else:
            for key, val in self.type_by_id.items():
                if not os.path.exists(val):
                    os.makedirs(val)


    @web.authenticated
    @gen.coroutine
    def get(self):
        return_data = yield tianchi.is_tianchi_joined(self.log, self.get_cookie('login_aliyunid_ticket'), tianchi_url, cookies=self.cookies)
        if return_data:
            self._get_tianchi_demo()
        else:
            self._get_normal_demo()

    @gen.coroutine
    def _get_normal_demo(self):
        self.log.warn('_get_normal_demo')
        if "dsw_debug" in os.environ:
            ticket = debug_login_aliyunid_ticket
            user_number = '1586990949331376'
        else:
            ticket = self.get_cookie('login_aliyunid_ticket');
            user_number = os.environ['dsw_userNumber'];
        self.log.warn('uid is %s, ticket is %s', user_number, ticket)
        data = yield self.builder.send_request(self.url + '/list', user_number, ticket, None, cookies=self.cookies)
        self.log.warn('data is %s', data)
        files = json.loads(data)
        self.log.warn('files is %s', files)
        if not files['data']:
            self.finish(json.dumps({}))
            return
        for file in files['data']:
            file['folder'] = self.type_by_id[file['type']]
        self.finish(json.dumps(files['data']))
        return

    @gen.coroutine
    def _get_tianchi_demo(self):
        self.log.warn('_get_tianchi_demo')
        if "dsw_debug" in os.environ:
            ticket = debug_login_aliyunid_ticket
            user_number = '1586990949331376'
        else:
            ticket = self.get_cookie('login_aliyunid_ticket');
            user_number = os.environ['dsw_userNumber'];
        self.log.warn('uid is %s, ticket is %s', user_number, ticket)
        files = yield self.builder.send_request_without_auth(self.tianchi_url + '/api/data/list', ticket, {}, cookies=self.cookies)
        self.log.warn('data is %s', files)
        # files = json.loads(data)
        # self.log.warn('files is %s', files)
        if not files['data'] or not files['data']['gameDatas']:
            self.finish(json.dumps({}))
            return
        for file in files['data']['gameDatas']:
            file['folder'] = self.type_by_id[file['type']]
        self.finish(json.dumps(files['data']['gameDatas']))
        return

    @web.authenticated
    @gen.coroutine
    def post(self):
        return_data = yield tianchi.is_tianchi_joined(self.log, self.get_cookie('login_aliyunid_ticket'), tianchi_url, cookies=self.cookies)
        if return_data:
            self._download_by_api_service()
        else:
            self._download_directly()

    @gen.coroutine
    def _download_by_api_service(self):
        self.log.warn('_download_by_api_service args is %s', self.get_json_body())
        data = self.get_json_body()
        if "dsw_debug" in os.environ:
            uid = debug_login_aliyunid_ticket
        else:
            uid = self.get_cookie('login_aliyunid_ticket')
        self.log.warn('uid is %s', uid)
        # url = self.tianchi_url + '/api/data/download?ticket=' + uid + '&name=' + data['path']
        parameters = urlencode({'ticket': uid, 'name': data['path']}, safe='/', quote_via=quote)
        url = self.tianchi_url + '/api/data/download'
        self.log.warn('parameters is %s', parameters)

        id = str(uuid.uuid1())
        if '/' in data['path']:
            id = id + data['path'].split('/')[-1]
        else:
            id = id + data['path']
        user_cookie = get_specific_cookie(self.cookies)
        progress_counter.download_async(prefix=self.type_by_id[data['type']], id=id, url=url, file_name=data['path'],
                                        parameters=parameters, log=self.log, cookies = user_cookie)
        self.finish(json.dumps({'id': id}))
        self.set_status(200)

    @gen.coroutine
    def _download_directly(self):
        self.log.warn('_download_directly args is %s', self.get_json_body())
        data = self.get_json_body()
        if "dsw_debug" in os.environ:
            ticket = debug_login_aliyunid_ticket
            user_number = '1586990949331376'
        else:
            ticket = self.get_cookie('login_aliyunid_ticket');
            user_number = os.environ['dsw_userNumber'];
        self.log.warn('uid is %s, ticket is %s', user_number, ticket)
        files = yield self.builder.send_request(self.url + '/' + str(data['id']) + '/detail', user_number, ticket, None, cookies=self.cookies)
        self.log.warn('response is %s', files)
        response = json.loads(files)
        self.log.warn('response json is %s', response)

        if not response['data']:
            self.finish(json.dumps(dict(message='call /demos/detail return error')))
            self.set_status(500)
            return

        if "dsw_debug" in os.environ:
            file_name = os.environ['dsw_test_folder'] + '/Demo/' + response['data']['url'].split('/')[-1]
        else:
            file_name = response['data']['url'].split('/')[-1]
        id = str(uuid.uuid1())
        if '/' in file_name:
            id = id + file_name.split('/')[-1]
        else:
            id = id + file_name

        self.log.info('file name is %s', file_name)
        user_cookie = get_specific_cookie(self.cookies)
        progress_counter.download_async(prefix=self.type_by_id[response['data']['type']], id=id,
                                        url=response['data']['url'], file_name=file_name, log=self.log, cookies = user_cookie)
        self.finish(json.dumps({'id': id}))
        self.set_status(200)


# The path for lab build.
demo_build_path = r"/lab/api/demo"
