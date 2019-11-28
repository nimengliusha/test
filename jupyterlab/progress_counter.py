from urllib.request import FancyURLopener

urlretrieve = FancyURLopener().retrieve

import requests
from contextlib import closing
from threading import Thread
import tarfile
import os
import json
import _thread
import traceback
import subprocess
import uuid


class ProgressCounter(object):
    def __init__(self):
        super(ProgressCounter, self).__init__()
        self.current_size_by_id = {}
        self.current_response_data_by_id = {}
        self.total_size_by_id = {}
        self.error_by_id = {}
        self.home_dir = '/home/admin/jupyter'

    def get_download_progress(self, log, id):
        if id in self.error_by_id:
            return {'status': 500, 'progress': self.error_by_id[id]}
        log.info(self.current_size_by_id)
        log.info(self.total_size_by_id)
        if not id in self.current_size_by_id or not id in self.total_size_by_id:
            return {'status': 200, 'progress': '0%'}
        if id in self.current_response_data_by_id and self.current_response_data_by_id[id] is not None:
            data = self.current_response_data_by_id[id]
        else:
            data = ''
            log.info("current_response_data_by_id", self.current_response_data_by_id)
        return {'status': 200,
                'progress': str(round(self.current_size_by_id[id] * 100 / self.total_size_by_id[id])) + '%',
                'data': data}

    def set_total_size_by_id(self, id, value):
        self.total_size_by_id[id] = value

    def refresh(self, id, count=1):
        self.current_size_by_id[id] += count

    def create_folder_if_necessary(self, log, folder_path):
        if not os.path.isdir(folder_path):
            log.warn('create folder %s', folder_path)
            os.makedirs(folder_path)

    def create_folder(self, log, prefix, file_name, need_decompress):
        file_name_without_suffix = ''
        if need_decompress:
            if file_name.endswith('.tar.gz'):
                file_name_without_suffix = file_name[:file_name.rfind('.tar.gz')]
            else:
                file_name_without_suffix = file_name
            if not file_name.endswith('.tar.gz'):
                file_name = file_name + '.tar.gz'
        file_name = self.home_dir + prefix + '/' + file_name
        log.info("file_name is %s", file_name)
        self.create_folder_if_necessary(log, os.path.dirname(file_name))
        return file_name, file_name_without_suffix

    def download(self, log, prefix, id, url, file_name, parameters, headers, need_decompress, cookies):
        file_name, file_name_without_suffix = self.create_folder(log, prefix, file_name, need_decompress)
        log.info("url is %s?%s", url, parameters)
        log.info("cookies is %s", cookies)
        # for k, v in cookies.iteritems():
        #     log.info("k and v is %s, %s", k, v)
        self.current_size_by_id[id] = 0
        self.current_response_data_by_id[id] = {}
        self.set_total_size_by_id(id, 100)
        # url = 'http://10.101.106.115/api/data/download?name=ruijin1&ticket=wU_TOTNChZBoeM1KJexdfb9zhYnsN5Zos6qISCrRt7mGxbigG2Cd4fWaCmBZHIzsgdZq64XXWQgyKFeuf0vpmV*s*CT58JlM_1t$w3sV$I1*3GXGW95cqyBACc30bK1oO5EgsxLfzmBmXerG_cppofNB0'
        # url = 'http://pai-for-security.oss-ap-southeast-1.aliyuncs.com/pmml%2Fa.tar.gz'
        with closing(requests.get(url, params=parameters, stream=True, headers=headers, cookies=cookies)) as response:
            try:
                log.info("response header is %s", response.headers)

                if response.status_code != 200:
                    body = json.loads(response.content.decode('utf8'))
                    log.error('status_code is not correct')
                    log.info("response status_code is %s", response.status_code)
                    log.info("response body is %s", response.content)
                    if 'errMsg' in body:
                        log.info("response msg is %s", body['errMsg'])
                        self.error_by_id[id] = body['errMsg']
                    elif 'message' in body:
                        log.info("response msg is %s", body['message'])
                        self.error_by_id[id] = body['message']
                    else:
                        self.error_by_id[id] = 'unknown error'
                    return
                content_size = int(response.headers['content-length'])
                log.info("id is %s, content is %s", id, content_size)
                self.set_total_size_by_id(id, content_size)
                with open(file_name, "wb") as file:
                    for data in response.iter_content(chunk_size=1024):
                        file.write(data)
                        self.refresh(id, count=len(data))
                if need_decompress:
                    dir = self.home_dir + prefix + '/' + file_name_without_suffix + '/'
                    log.info('decompress dir is %s', dir)
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                    subprocess.check_call(["tar", "-zvxf", file_name, '-C', dir], stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL)
                    os.remove(file_name)
                log.info('download success')
            except Exception as inst:
                log.error(u'Error while saving file: %s', inst, exc_info=True)
                if hasattr(inst, 'args') and len(inst.args) > 0:
                    self.error_by_id[id] = inst.args[1]
                else:
                    self.error_by_id[id] = str(inst)

    def upload(self, log, id, url, file_name, parameters, headers, cookies=None):
        if '/' in file_name:
            file_name_without_path = file_name.split('/')[-1]
        else:
            file_name_without_path = file_name
        if not file_name.startswith('/'):
            file_name = self.home_dir + '/' + file_name
        else:
            file_name = self.home_dir + file_name
        log.info("url is %s", url)
        log.info("file_name is %s", file_name)
        log.info("file_name_without_path is %s", file_name_without_path)
        self.current_size_by_id[id] = 0
        # todo test
        # url = 'http://daily.notebook.data.aliyun.test/api/data/submit?ticket=58slMT1tJw3_V$$1*sGXIW93cqGBA5c3ycKCk*6fRF_q0LnfbgU8S6Ai2of_BNpwU_TOTNChZBoeM1KJexdfb9zhYnsN5Zos6qISCrRt7mGxbigG2Cd4fWaCmBZHIzsgdZq64XXWQgyKFeuf0vpmV*C*0&name=ruijin'
        self.set_total_size_by_id(id, 100)
        try:
            upload_file = {'data': (file_name_without_path, open(file_name, 'rb'))}
            r = requests.post(url, params=parameters, files=upload_file, headers=headers, stream=True, cookies=cookies)
            log.info('upload response is %s', r.content)
            response = json.loads(r.content)
            if response['errCode'] == 0:
                self.current_size_by_id[id] = 100
                if 'data' in response and response['data'] is not None and 'notebookInfo' in response['data']:
                    log.info('upload success')
                    self.current_response_data_by_id[id] = response['data']['notebookInfo']
                else:
                    log.info('upload success with null data')
                    self.current_response_data_by_id[id] = {}
            else:
                log.info('upload fail', response['errMsg'])
                self.error_by_id[id] = response['errMsg']
        except:
            traceback.print_exc()
            self.error_by_id[id] = 'upload error'

    def download_async(self, prefix, url, file_name, id, parameters={}, headers={}, log=None,
                       need_decompress=True, cookies=None):
        _thread.start_new_thread(self.download,
                                 (log, prefix, id, url, file_name, parameters, headers, need_decompress, cookies))

    def upload_async(self, log, id, url, file_name, parameters, headers, cookies=None):
        _thread.start_new_thread(self.upload, (log, id, url, file_name, parameters, headers, cookies))


progress_counter = ProgressCounter()
