"""
JupyterLab prometheus: proxy through to local prometheus agent
"""

from notebook.utils import url_path_join
from urllib import request

__version__ = '0.0.1'

import os, json
from tornado import web
from notebook.base.handlers import APIHandler

def _jupyter_server_extension_paths():
  return [{
    'module': __name__ 
  }]

def load_jupyter_server_extension(nb_server_app):
  web_app = nb_server_app.web_app
  host_pattern = '.*$'
  base_url = web_app.settings['base_url']
  metric_proxy = url_path_join(base_url, '/metrics')
  web_app.add_handlers(host_pattern,
    [(metric_proxy, MetricsProxyHandler)])

class MetricsProxyHandler(APIHandler):
  def get(self):
    uri = "http://127.0.0.1:9100/metrics"
    req = request.Request(uri)
    with request.urlopen(req) as resp:
      self.finish(resp.read())
