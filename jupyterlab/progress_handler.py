"""Tornado handlers for frontend config storage."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json

from notebook.base.handlers import APIHandler
from tornado import gen, web

from .progress_counter import progress_counter


class ProgressBuilder(object):
    def __init__(self, log, core_mode, app_dir):
        return



class ProgressHandler(APIHandler):
    def initialize(self, builder):
        return

    @web.authenticated
    @gen.coroutine
    def get(self):
        id = self.get_argument('id', None)
        self.finish(json.dumps(progress_counter.get_download_progress(self.log, id)))


# The path for lab build.
progress_build_path = r"/lab/api/status"
