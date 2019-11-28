# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from os import path as osp
import os
from .debug_env import *
import json
from tornado import gen, web
from .openapi import send_request, get_download_request
from .openapi import forward_request_without_auth
import os

tianchi_url = 'http://' + os.environ['dsw_dswDomain']

class Tianchi(object):

    def __init__(self):
        self._is_joined = 0

    def send_tianchi_request(self, log, url, uid, ticket, arg, cookies=None):
        # if arg:
        #     arg = arg + '&userNumber=' + uid + '&ticket=' + ticket
        # else:
        #     arg = 'userNumber=' + uid + '&ticket=' + ticket
        arg['userNumber'] = uid
        arg['ticket'] = ticket
        # key = os.environ['dsw_serviceId']
        # token = os.environ['dsw_token']
        # log.warn('token is %s', token)
        # log.warn('key is %s', key)
        log.warn('arg is %s', arg)
        resp = send_request(log, url, arg, cookies=cookies)
        # resp = forward_request_without_auth(log, url, arg, cookies=cookies)
        # resp = send_request_without_auth(log, url, arg, cookies=cookies)
        log.warn('send_request success')
        log.warn(resp)
        return resp

    @gen.coroutine
    def send_request(self, log, url, uid, ticket, arg, cookies=None):
        if arg:
            arg = arg + '&userNumber=' + uid + '&ticket=' + ticket
        else:
            arg = 'userNumber=' + uid + '&ticket=' + ticket
        key = os.environ['dsw_serviceId']
        token = os.environ['dsw_token']
        log.warn('dsw_token is %s', token)
        log.warn('key is %s', key)
        resp = send_request(log, key, token, url, arg, cookies=cookies)
        log.warn('send_request success')
        log.warn(resp)
        raise gen.Return(resp)

    def is_tianchi_joined_without_auth(self, log, cookie_ticket, cookies=None):
        if "dsw_debug" in os.environ:
            ticket = debug_login_aliyunid_ticket
            user_number = '1586990949331376'
        else:
            ticket = cookie_ticket
            user_number = os.environ['dsw_userNumber']
        log.warn('is joined uid is %s, ticket is %s', user_number, ticket)
        data = self.send_tianchi_request(log, tianchi_url + '/games/player/joined', user_number, ticket, {}, cookies=cookies)
        log.warn('is joined data is %s', data)
        files = json.loads(data)
        log.warn('files is %s', files)
        if not files['data'] or len(files['data']) == 0:
            log.info('is joined False')
            return False
        else:
            log.info('is joined True')
            return True

    @gen.coroutine
    def is_tianchi_joined(self, log, cookie_ticket, tianchi_url, cookies=None):
        if self._is_joined == 0:
            if "dsw_debug" in os.environ:
                ticket = debug_login_aliyunid_ticket
                user_number = '1586990949331376'
            else:
                ticket = cookie_ticket
                user_number = os.environ['dsw_userNumber']
            log.warn('is joined uid is %s, ticket is %s', user_number, ticket)
            data = yield self.send_request(log, tianchi_url + '/games/player/joined', user_number, ticket, None, cookies=cookies)
            log.warn('is joined data is %s', data)
            files = json.loads(data)
            log.warn('files is %s', files)
            if not files['data'] or len(files['data']) == 0:
                self._is_joined = 1
                log.info('is joined False')
                raise gen.Return(False)
            else:
                self._is_joined = 2
                log.info('is joined True')
                raise gen.Return(True)
        elif self._is_joined == 1:
            log.info('is joined False')
            raise gen.Return(False)
        else:
            log.info('is joined True')
            raise gen.Return(True)

tianchi = Tianchi()
