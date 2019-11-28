cookies_whitelist = ['c_token','ck2','login_aliyunid_ticket']
header_blacklist = ['Cookie']


def get_specific_cookie(cookies):
    cookie_obj = {}
    for key, value in cookies.items():
        if key in cookies_whitelist:
            cookie_obj[key] = value.value
    return cookie_obj


def get_header_without_cookie(headers):
    header_obj = {}
    for key, value in headers.items():
        if key not in header_blacklist:
            header_obj[key] = value
    return header_obj
