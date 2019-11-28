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
from .env import HOME_DIR, DATASET_DOWNLOAD_DIR
import uuid
class CommunityDatasetDownloadBuilder(CommonBuilder):
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
        self.domain = os.environ['dsw_dswDomain'];

    def get_file_name(self, path):
        end_location = path.rfind('/')
        if end_location >= 0:
            return path[end_location + 1:]
        else:
            return path


class CommunityDatasetDownloadHandler(APIHandler):
    def initialize(self, builder):
        self.builder = builder
        self.url = 'http://' + builder.domain

    @not_tianchi_user
    @web.authenticated
    @gen.coroutine
    def post(self):
        self.log.warn('args is %s', self.get_json_body())
        data = self.get_json_body()
        if "dsw_debug" in os.environ:
            uid = debug_login_aliyunid_ticket
        else:
            uid = self.get_cookie('login_aliyunid_ticket')
        dataId = str(data['dataId'])
        fileId = str(data['fileId'])
        folder_path = '/' + DATASET_DOWNLOAD_DIR + '/' + dataId
        self.log.warn('uid is %s', uid)
        url = self.url + '/dev/downloadDataset/stream?ticket=' + uid + '&dataId=' + dataId + '&fileId=' + fileId
        self.log.warn('url is %s', url)
        file_name = self.builder.get_file_name(data['name'])
        self.log.warn('file name is %s', file_name)
        unique_id = str(uuid.uuid1())
        progress_counter.download_async(id=unique_id, log=self.log, prefix=folder_path, url=url, file_name=file_name,
                                        need_decompress=False)
        self.finish(json.dumps({'id': unique_id}))
        self.set_status(200)


# The path for lab build.
community_dataset_download_path = r"/lab/api/community/dataset/download"
