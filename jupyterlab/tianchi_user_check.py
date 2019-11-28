import functools
from .tianchi_service import tianchi, tianchi_url

from tornado import gen, web



def tianchi_user(func):
    @gen.coroutine
    @functools.wraps(func)
    def is_tianchi_user(*args, **kwargs):
        return_data = yield tianchi.is_tianchi_joined(args[0].log, args[0].get_cookie('login_aliyunid_ticket'), tianchi_url, args[0].cookies)
        if return_data:
            args[0].log.warn('pass tianchi_user')
            return func(*args, **kwargs)
    return is_tianchi_user


def not_tianchi_user(func):
    @gen.coroutine
    @functools.wraps(func)
    def is_tianchi_user(*args, **kwargs):
        return_data = yield tianchi.is_tianchi_joined(args[0].log, args[0].get_cookie('login_aliyunid_ticket'), tianchi_url, args[0].cookies)
        if not return_data:
            args[0].log.warn('pass not_tianchi_user')
            return func(*args, **kwargs)
    return is_tianchi_user