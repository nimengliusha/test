"""Tornado handlers for frontend config storage."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from notebook.base.handlers import APIHandler
from .common_builder import CommonBuilder
from .tianchi_service import *
from .env import HOME_DIR


class FileExistBuilder(CommonBuilder):
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


class FileExistHandler(APIHandler):
    def initialize(self, builder):
        self.builder = builder

    @web.authenticated
    @gen.coroutine
    def get(self):
        self.log.warn('enter FileExistHandler')
        file_path = self.get_argument('file', None)
        self.finish(json.dumps({'exists': os.path.isfile(HOME_DIR + '/' + file_path)}))


# The path for lab build.
file_exists_path = r"/lab/api/file/exists"
