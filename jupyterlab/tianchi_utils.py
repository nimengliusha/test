# # -*- coding: utf-8 -*-
# from .debug_env import *
# import json
# import os
# from .tianchi_service import tianchi, tianchi_url
#
# tianchi_url = 'http://' + os.environ['dsw_dswDomain']
#
# def send_tianchi_request(log, url, uid, ticket, arg):
#     if arg:
#         arg = arg + '&userNumber=' + uid + '&ticket=' + ticket
#     else:
#         arg = 'userNumber=' + uid + '&ticket=' + ticket
#     key = os.environ['dsw_serviceId']
#     token = os.environ['dsw_token']
#     log.warn('token is %s', token)
#     log.warn('key is %s', key)
#     resp = tianchi.send_request_without_auth(log, url, arg)
#     log.warn('send_request success')
#     log.warn(resp)
#     return resp
#
#
# def is_tianchi_joined(log, cookie_ticket):
#     if "dsw_debug" in os.environ:
#         ticket = debug_login_aliyunid_ticket
#         user_number = '1586990949331376'
#     else:
#         ticket = cookie_ticket
#         user_number = os.environ['dsw_userNumber']
#     log.warn('is joined uid is %s, ticket is %s', user_number, ticket)
#     data = send_tianchi_request(log, tianchi_url + '/games/player/joined', user_number, ticket, None)
#     log.warn('is joined data is %s', data)
#     files = json.loads(data)
#     log.warn('files is %s', files)
#     if not files['data'] or len(files['data']) == 0:
#         log.info('is joined False')
#         return False
#     else:
#         log.info('is joined True')
#         return True
