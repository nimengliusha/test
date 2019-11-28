from concurrent.futures import ThreadPoolExecutor
import json
from threading import Event

import subprocess
from subprocess import Popen, PIPE

from notebook.base.handlers import APIHandler
from tornado import gen, web
from tornado.concurrent import run_on_executor

from .commands import build, clean, build_check
from urllib import request, parse
import json
from pathlib import Path
from .openapi import send_request
import os
from .common_builder import CommonBuilder
from .debug_env import *

import re
import logging

class GitOperBuilder(CommonBuilder):
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
        self.root_dir = os.path.realpath('/home/admin/jupyter')
        user_name = os.environ['dsw_userNumber']
        user_email = user_name + '@example.com'
        self.log.warn(GitOperHandler.submit_comm('GIT_TERMINAL_PROMPT=0 git config user.name "' + user_name + '"', self.root_dir))
        self.log.warn(GitOperHandler.submit_comm('GIT_TERMINAL_PROMPT=0 git config user.email "' + user_email + '"', self.root_dir))
        # 程序启动的时候初始化GIT内容
        result = GitOperHandler.submit_comm('ls .git/init.lock', self.root_dir)
        if not result['isSuccess']:
            self.log.warn('Git init begin')
            self.log.warn(GitOperHandler.submit_comm('GIT_TERMINAL_PROMPT=0 git init', self.root_dir))
            self.log.warn(GitOperHandler.submit_comm('GIT_TERMINAL_PROMPT=0 git add --all', self.root_dir))
            self.log.warn(GitOperHandler.submit_comm('GIT_TERMINAL_PROMPT=0 git commit -m \'initial project version\'', self.root_dir))
            self.log.warn(GitOperHandler.submit_comm('touch .git/init.lock', self.root_dir))
            self.log.warn(GitOperHandler.submit_comm('GIT_TERMINAL_PROMPT=0 git config user.name "' + user_name + '"',
                                                     self.root_dir))
            self.log.warn(GitOperHandler.submit_comm('GIT_TERMINAL_PROMPT=0 git config user.email "' + user_email + '"',
                                                     self.root_dir))
            self.log.warn('Git init finished')
        else:
            self.log.warn('Git have been init')


class GitOperHandler(APIHandler):
    def initialize(self, builder):
        self.root_dir = os.path.realpath('/home/admin/jupyter')
        self.builder = builder

    @web.authenticated
    def get(self):
        file_path = '"' + self.get_argument('path') + '"'
        version_list = self.submit_comm('GIT_TERMINAL_PROMPT=0 git log --no-walk --tags --pretty="%h %d %s" ' + file_path, self.root_dir)
        result = []
        if version_list['isSuccess']:
            for line in version_list['msg']:
                line_list = line.split(' ', 1)
                one_record = {}
                one_record['version'] = line_list[0]
                one_record['text'] = re.sub(r'\([^)]*\)', '', line_list[1]).strip()
                result.append(one_record)
            self.finish(json.dumps(result))
            self.set_status(200)
        else:
            self.finish(json.dumps(version_list['msg']))
            self.set_status(500)

    @web.authenticated
    @gen.coroutine
    def post(self):
        method = self.get_argument('method')
        if method == 'revert':
            self._git_revert()
        elif method == 'commit':
            self._git_commit()
        elif method == 'delete':
            self._git_delete()
        else:
            self.finish('Params error')
            self.set_status(500)

    def _git_delete(self):
        version = self.get_argument('version')
        result = self.submit_comm('GIT_TERMINAL_PROMPT=0 git tag -d ' + version, self.root_dir)
        if result['isSuccess']:
            self.finish(json.dumps({'isSuccess': True}))
            self.set_status(200)
        else:
            self.finish(result)
            self.set_status(500)

    def _git_revert(self):
        file_path = '"' + self.get_argument('path') + '"'
        version = self.get_argument('version')
        result = self.submit_comm('GIT_TERMINAL_PROMPT=0 git checkout ' + version + ' ' + file_path, self.root_dir)
        if result['isSuccess']:
            self.finish(json.dumps({'isSuccess': True}))
            self.set_status(200)
        else:
            self.finish(result)
            self.set_status(500)

    def _git_commit(self):
        file_path = '"' + self.get_argument('path') + '"'
        message = '"' + self.get_argument('message') + '"'
        result = self.submit_comm('GIT_TERMINAL_PROMPT=0 git add ' + file_path, self.root_dir)
        logging.info("Git add result: " + json.dumps(result))
        if result['isSuccess']:
            result = self.submit_comm('GIT_TERMINAL_PROMPT=0 git commit -m ' + message, self.root_dir)
            logging.info("Git commit result: " + json.dumps(result))
            if result['isSuccess']:
                # 去除类似[master (root-commit) 868acf8] XXX 中间的干扰内容
                version = re.sub(r'\s*\([^)]*\)\s*', ' ', result['msg'][0]).strip()
                version = version.split(' ', 2)
                if len(version) > 2:
                    version = version[1].strip(']')
                    result = self.submit_comm('GIT_TERMINAL_PROMPT=0 git tag ' + version + ' ' + version, self.root_dir)
                    logging.info("Git tag result: " + json.dumps(result))
                    if result['isSuccess']:
                        self.finish(json.dumps({'isSuccess': True}))
                        self.set_status(200)
                    else:
                        self.finish(result)
                        self.set_status(500)
                else:
                    self.finish(json.dumps({'isSuccess': False}, {'msg': 'version format error, the version is ' + result['msg'][0]}))
                    self.set_status(500)
            else:
                self.finish(result)
                self.set_status(500)
        else:
            self.finish(result)
            self.set_status(500)

    @staticmethod
    def submit_comm(cmd, path):
        logging.info("Cmd run: " + cmd)
        p = subprocess.Popen(
            [cmd],
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            cwd=path,
        )
        output, error = p.communicate()
        if p.returncode != 0:
            return {
                "isSuccess": False,
                "msg": error.decode('utf-8').strip()
            }
        else:
            return {
                "isSuccess": True,
                "msg": output.decode("utf-8").splitlines()
            }


# The path for lab build.
git_oper_path = r"/lab/api/git"
