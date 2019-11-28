import json
import os
from http import HTTPStatus
from pathlib import Path
from notebook.base.handlers import APIHandler
from ..common_builder import CommonBuilder
from tornado import gen, web


class FileUploadBuilder(CommonBuilder):

    def __init__(self, log, core_mode, app_dir):
        super().__init__(log)
        self.log = log
        self.core_mode = core_mode
        self.app_dir = app_dir


class FileUploadHanler(APIHandler):
    """
      :param
    """
    tus_api_version = '1.0.0'
    tus_api_version_supported = ['1.0.0', ]
    tus_api_extensions = ['creation', 'termination', 'file-check']
    # on_finish = None
    upload_config = dict()
    file_info = dict()
    default_path = '/home/admin/jupyter/'

    def initialize(self, builder):
        self.builder = builder
        # path = os.path.dirname(os.path.abspath(__file__))
        # path = os.path.join(path, 'settings.json')
        # try:
        #     with open(path, 'r') as f:
        #         self.upload_config = json.load(f)
        #         self.log.info(self.upload_config)
        # except Exception as e:
        #     self.log.error(e)


    def get_tus_response(self):
        response = dict()
        response['Tus-Resumable'] = self.tus_api_version
        response['Tus-Version'] = ",".join(self.tus_api_version_supported)
        response['Tus-Extension'] = ",".join(self.tus_api_extensions)
        # response['Tus-Max-Size'] = settings.TUS_MAX_FILE_SIZE
        response['Access-Control-Allow-Origin'] = "*"
        response['Access-Control-Allow-Methods'] = "PATCH,HEAD,GET,POST,OPTIONS"
        response['Access-Control-Expose-Headers'] = "Tus-Resumable,upload-length,upload-metadata,Location,Upload-Offset"
        response['Access-Control-Allow-Headers'] = "Tus-Resumable,upload-length,upload-metadata,Location,Upload-Offset,content-type"
        response['Cache-Control'] = 'no-store'

        return response

    @web.authenticated
    @gen.coroutine
    def get(self, name):

        pass

    @web.authenticated
    @gen.coroutine
    def head(self, name):
        """
        :param name
        :return response:
        """
        self.log.info('upload file head filename %s', name)
        self.print_headers()
        #Content-Type: application/offset+octet-stream

        path = self.upload_path()

        #check file and info file
        bin_file = os.path.join(path, name)
        # info_file = os.path.join(path, "." + name + ".info")

        offset = 0
        bin_path = Path(bin_file)
        if bin_path.exists():
            offset = os.path.getsize(bin_file)

        # get head length md5
        # Content-Length
        length = self.request.headers.get('Upload-Length')
        md5 = self.request.headers.get('md5')
        self.file_info['name'] = name
        self.file_info['length'] = length
        if md5:
            self.file_info['md5'] = md5

        # self.setHeaders()
        self.set_header('upload-offset', offset)
        self.set_header('Access-Control-Expose-Headers', 'upload-length,upload-metadata,Location,Upload-Offset')
        self.finish()

    @web.authenticated
    @gen.coroutine
    def post(self, name):
        self.print_headers()

        self.set_header('upload-offset', 0)
        self.set_header('Location', name)

        self.finish()

    @web.authenticated
    @gen.coroutine
    def delete(self, name):
        self.log.info('upload file delete filename %s', name)
        self.print_headers()

        path = self.upload_path()

        bin_file = os.path.join(path, name)
        bin_path = Path(bin_file)

        if bin_path.exists():
            os.remove(bin_file)

        self.finish()

    @web.authenticated
    @gen.coroutine
    def patch(self, name):
        self.log.info('upload file patch filename %s', name)

        self.print_headers()
        data = self.request.body

        path = self.upload_path()

        # check file and info file
        bin_file = os.path.join(path, name)

        offset = 0
        bin_path = Path(bin_file)
        if bin_path.exists():
            offset = os.path.getsize(bin_file)

        # Upload-Offset check
        upload_offset = int(self.request.headers.get('Upload-Offset'))
        # make sure we're in sync, conflict 409
        if offset != upload_offset:
            self.set_status(HTTPStatus.CONFLICT)
            self.set_header('Upload-Offset', offset)
            self.finish()
            return

        # Content-Length
        with open(bin_file, "ab") as file:
            file.write(data)

        offset = os.path.getsize(bin_file)

        self.set_header('Upload-Offset', offset)

        self.set_status(HTTPStatus.NO_CONTENT)
        self.finish()

    def set_headers(self):
        for key, value in self.get_tus_response().items():
            self.set_header(key, value)

    def print_headers(self):
        for i in self.request.headers:
            self.log.info(i + " : " + self.request.headers[i])

    def upload_path(self):
        """
         get upload path, if empty ,return default
        :return:
        """
        path = self.request.headers.get('Upload-Path')
        if path and len(path) > 0:
            return os.path.join(self.default_path, path)

        return self.default_path


file_upload_path = r"/lab/api/file_upload/([^/]+?)"
