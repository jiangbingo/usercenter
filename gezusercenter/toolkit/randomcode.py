# -- encoding: utf-8 --
__author__ = 'PD-002'

import binascii
import os
import random
import time

from django.utils import timezone


def get_random_code(length=8, symbol=False):
    """generate a security key"""

    char_set = {
        'nums': '0123456789',
        'small': 'abcdefghijklmnopqrstuvwxyz',
        'big': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    }

    if symbol:
        char_set['other'] = '!@#$%&*()+?<>'
    password = []
    while len(password) < length:
        key = random.choice(char_set.keys())
        a_char = os.urandom(1)
        if a_char in char_set[key]:
            if on_check_previous_char(password, char_set[key]):
                continue
            else:
                password.append(a_char)
    return ''.join(password)

def on_check_previous_char(password, current_char_set):
    """检测前一个字符是否跟生成的一样"""

    index = len(password)
    if index == 0:
        return False
    else:
        prev_char = password[index - 1]
        if prev_char in current_char_set:
            return True
        else:
            return False

def get_random_str(length=32):
    count = abs(int(length/32))
    if 0 == count:
        count = 1
    return binascii.b2a_base64(os.urandom(24 * count))[:-1]

def get_token():
    return get_random_str(64)

def get_license(method = "cop"):
    # 获取分类下数量统计count
    count = 0
    return "sdgdfhryhrfbg"

def get_app_secret(method="cop"):
    # cop:商家 nus:普通用户 dsn:设计师
    index = str(time.time()).replace('.', '')
    return method + index


def utc2local(utc_st):
    return timezone.localtime(utc_st)

if __name__ == "__main__":
    print "token", get_token()
    print "license", get_license()
    print "secret", get_app_secret()

    # token = get_token()
    # license = get_license()
    # app_secret = get_app_secret()
    #
    # print token + license + app_secret + hex(len(token))[2:] + hex(len(license))[2:] + hex(len(app_secret))[2:]
    # print "{:0>2}".format(hex(len(token))[2:])
    # print "{:0>2}".format(hex(len(license))[2:])
    # print "{:0>2}".format(hex(len(app_secret))[2:])
