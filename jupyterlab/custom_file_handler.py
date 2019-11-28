from notebook.files.handlers import FilesHandler
from tornado import gen
from .tianchi_service import tianchi, tianchi_url
import mimetypes
import json

try:  # PY3
    from base64 import decodebytes
except ImportError:  # PY2
    from base64 import decodestring as decodebytes

from tornado import web
from notebook.base.handlers import IPythonHandler


class CustomFileHandler(IPythonHandler):
    @property
    def content_security_policy(self):
        # In case we're serving HTML/SVG, confine any Javascript to a unique
        # origin so it can't interact with the notebook server.
        return super(IPythonHandler, self).content_security_policy + \
               "; sandbox allow-scripts"

    # def get(self, path, include_body=True):
    #     try:
    #         super().get(path, include_body)
    #     except:
    #         import traceback
    #         traceback.print_exc()

    @web.authenticated
    @gen.coroutine
    def head(self, path):
        super().head(path)
        self.get(path, include_body=False)

    @web.authenticated
    @gen.coroutine
    def get(self, path, include_body=True):
        return_data = yield tianchi.is_tianchi_joined(self.log, self.get_cookie('login_aliyunid_ticket'), tianchi_url)
        if not return_data:
            cm = self.contents_manager
            if cm.is_hidden(path) and not cm.allow_hidden:
                self.log.info("Refusing to serve hidden file, via 404 Error")
                raise web.HTTPError(404)

            path = path.strip('/')
            if '/' in path:
                _, name = path.rsplit('/', 1)
            else:
                name = path

            model = cm.get(path, type='file', content=include_body)

            if self.get_argument("download", False):
                self.set_attachment_header(name)

            # get mimetype from filename
            if name.endswith('.ipynb'):
                self.set_header('Content-Type', 'application/x-ipynb+json')
            else:
                cur_mime = mimetypes.guess_type(name)[0]
                if cur_mime == 'text/plain':
                    self.set_header('Content-Type', 'text/plain; charset=UTF-8')
                elif cur_mime is not None:
                    self.set_header('Content-Type', cur_mime)
                else:
                    if model['format'] == 'base64':
                        self.set_header('Content-Type', 'application/octet-stream')
                    else:
                        self.set_header('Content-Type', 'text/plain; charset=UTF-8')

            if include_body:
                if model['format'] == 'base64':
                    b64_bytes = model['content'].encode('ascii')
                    self.write(decodebytes(b64_bytes))
                elif model['format'] == 'json':
                    self.write(json.dumps(model['content']))
                else:
                    self.write(model['content'])
                self.flush()
        else:
            raise Exception('not allowed for tianchi user')
