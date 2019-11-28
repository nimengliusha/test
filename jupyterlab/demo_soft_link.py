# """Tornado handlers for frontend config storage."""
#
# # Copyright (c) Jupyter Development Team.
# # Distributed under the terms of the Modified BSD License.
#
# from notebook.base.handlers import APIHandler
# from tornado import gen, web
# import json
# from .common_builder import CommonBuilder
# import subprocess
#
#
# class SoftLinkBuilder(CommonBuilder):
#
#     def __init__(self, log, core_mode, app_dir):
#         super().__init__(log)
#         self.log = log
#         self.core_mode = core_mode
#         self.app_dir = app_dir
#
#
# class SoftLinkHandler(APIHandler):
#     def initialize(self, builder):
#         self.builder = builder
#
#     @web.authenticated
#     @gen.coroutine
#     def get(self):
#         folder = self.get_argument('folder', None)
#         try:
#             # ln -s /mnt/file/opensearch/documents/%s/ ~/datalab/\n
#             subprocess.check_call(["ln", "-s", "/mnt/file/opensearch/documents/" + folder, '~/datalab/'],
#                                   stdout=subprocess.DEVNULL,
#                                   stderr=subprocess.DEVNULL)
#             self.log.info('ln success')
#         except Exception as inst:
#             self.log.error(u'Error while ln file: %s', inst, exc_info=True)
#             self.finish(json.dumps({'success': False, 'error': str(inst)}))
#
#         self.finish(json.dumps({'success': True}))
#
#
# # The path for lab build.
# demo_soft_link_path = r"/lab/api/demo/softlink"
