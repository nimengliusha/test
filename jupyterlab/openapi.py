import hashlib
import time
import urllib
import http, urllib.request, urllib.parse
import requests
import tornado
from .cookie_utils import *

def sign(log, token, qs):
    if qs:
        qs = urllib.parse.unquote(qs) \
            # .decode(encoding="utf-8", errors="strict")
    log.warn("Signing string start - %s", qs)
    arr = qs.split('&') if qs else []
    arr = sorted(arr)
    res = '{1}:{0}:{1}'.format('&'.join(arr), token)
    log.warn("Signing string - %s", res)
    return hashlib.sha256(res.encode("utf-8")).hexdigest()


def sign_query(log, query, base_key, token):
    t = time.time()
    qs = "baseKey={0}&timestamp={1}".format(base_key, int(t * 1000))
    qs = '{0}&{1}'.format(query, qs) if query else qs
    return qs, sign(log, token, qs)


def send_request(log, base_key, token, url_base, query=None, data=None, cookies=None, method='GET'):
    qs, signature = sign_query(log, query, base_key, token)
    log.warn("Query String: %s", qs)
    log.warn("Signature: %s", signature)
    # cookie_str = ''
    # for key, value in cookies.items():
    #     log.warn("key: %s, value: %s", key, value.value)
    #     cookie_str=cookie_str+key+'='+value.value+';'
    # headers = {'signature': signature, "Cookie": cookie_str}
    # # log.warn("headers: %s", headers)
    #
    # log.warn('url is %s', url)
    # log.warn('cookie is %s', cookie_str)
    # req = urllib.request.Request('{0}?{1}'.format(url_base, qs), data=data, headers=headers)
    # if method not in ('GET', 'POST'):
    #     req.get_method = lambda: method
    # response = urllib.request.urlopen(req)
    # return response.read()
    url = '{0}?{1}'.format(url_base, qs)
    headers = {'signature': signature}
    user_cookie = get_specific_cookie(cookies)
    log.warn("cookies: %s", user_cookie)
    headers_filtered = get_header_without_cookie(headers)
    if method == 'GET':
        response = requests.get(url, cookies=user_cookie, headers=headers_filtered)
    elif method =='POST':
        response = requests.post(url, cookies=user_cookie, headers=headers_filtered, data = data)
    dd= response.content
    log.warn("dd: %s", dd)
    return dd

def forward_request_without_auth(log, url_base, query={}, data={}, headers={}, cookies={}, method='GET'):
    query_parameter = ''
    for key, val in query.items():
        if query_parameter == '':
            query_parameter = key + '=' + tornado.escape.to_unicode(val[0])
        else:
            query_parameter = query_parameter + '&' + key + '=' + tornado.escape.to_unicode(val[0])
    log.info('query_parameter is %s', query_parameter)
    user_cookie = get_specific_cookie(cookies)
    url = '{0}?{1}'.format(url_base, query_parameter)
    log.info('url is %s', url)
    log.info('user_cookie is %s', user_cookie)
    headers_filtered = get_header_without_cookie(headers)
    log.info('header is %s', headers_filtered)
    if method == 'GET':
        res = requests.get(url, cookies=user_cookie, headers=headers_filtered)
    else:
        res = requests.post(url, cookies=user_cookie, data=data, headers=headers_filtered)
    log.info('res is %s', res)
    return res.json()


# def send_request_without_auth(log, url_base, query=None, data=None, method='GET', cookies={}):
#     log.warn('url is %s?%s', url_base, query)
#     req = urllib.request.Request('{0}?{1}'.format(url_base, query), data=data)
#     if method not in ('GET', 'POST'):
#         req.get_method = lambda: method
#     response = urllib.request.urlopen(req)
#     return response.read()


def get_download_request(log, base_key, token, url_base, query=None, data=None, method='GET'):
    qs, signature = sign_query(log, query, base_key, token)
    log.warn("Query String: %s", qs)
    log.warn("Signature: %s", signature)
    headers = {'signature': signature}
    log.warn('url is %s %s', url_base, qs)
    query = '{0}?{1}'.format(url_base, qs)
    log.warn('query is %s', query)
    return query, headers


if __name__ == '__main__':
    import os

    os.makedirs('~/Demo/aa/bb')
