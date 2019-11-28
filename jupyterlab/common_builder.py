"""Tornado handlers for frontend config storage."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from tornado import gen
from .openapi import *
import os


class CommonBuilder:
    def __init__(self, log):
        self.log = log

    @gen.coroutine
    def send_request(self, url, uid, ticket, arg, cookies):
        if arg:
            arg = arg + '&userNumber=' + uid + '&ticket=' + ticket
        else:
            arg = 'userNumber=' + uid + '&ticket=' + ticket
        key = os.environ['dsw_serviceId']
        token = os.environ['dsw_token']
        self.log.warn('token is %s', token)
        self.log.warn('key is %s', key)
        resp = send_request(self.log, key, token, url, arg, cookies=cookies)
        self.log.warn('send_request success')
        self.log.warn(resp)
        raise gen.Return(resp)

    @gen.coroutine
    def send_request_without_auth(self, url, ticket, arg={}, cookies=None):
        # if arg:
        #     arg = arg + '&ticket=' + ticket
        # else:
        #     arg = 'ticket=' + ticket
        arg['ticket'] = ticket
        resp = forward_request_without_auth(self.log, url, arg, cookies=cookies)
        # resp = send_request_without_auth(self.log, url, arg, cookies=cookies)
        self.log.warn(resp)
        raise gen.Return(resp)
