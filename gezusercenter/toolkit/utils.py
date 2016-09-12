# -- encoding: utf-8 --
__author__ = 'PD-002'
import datetime
import os
from hashlib import md5

from django.conf import settings


def get_models_path(*args):
    today = datetime.date.today()
    return os.path.join(os.path.join(os.path.join('models', '%s' % today.year), '%s' % today.month), '%s' % today.day)

def get_resources_path(*args):
    today = datetime.date.today()
    return os.path.join(os.path.join(os.path.join('resources', '%s' % today.year), '%s' % today.month),
                        '%s' % today.day)

def get_models_base_path(*args):
    today = datetime.date.today()
    return os.path.join(os.path.join(settings.BASE_DIR, "media"),
                        os.path.join(os.path.join(os.path.join('models', '%s' % today.year),
                                                  '%s' % today.month), '%s' % today.day))

ROLE_GROUP = ['普通用户', '设计师', '电商', '商铺', '装修公司', '厂家']
def encode_role(roles):
    role_array = []
    for index in range(len(ROLE_GROUP)):
        if index in roles:
            role_array.append('%s' % 1)
        else:
            role_array.append('%s' % 0)
    role_array.reverse()
    return int(''.join(role_array), 2)

def encode_role_unicode(roles):
    role_array = []
    for index in range(len(ROLE_GROUP)):
        if ROLE_GROUP[index] in roles:
            role_array.append('%s' % 1)
        else:
            role_array.append('%s' % 0)
    role_array.reverse()
    return int(''.join(role_array), 2)

def decode_role(role):
    role_array = [r=='1' for r in bin(role).replace('0b','')]
    role_array.reverse()
    roles = []
    for index in range(len(role_array)):
        if index < len(ROLE_GROUP) and role_array[index]:
            roles.append(index)
    return roles

def decode_role_unicode(role):
    role_array = [r == '1' for r in bin(role).replace('0b', '')]
    role_array.reverse()
    roles = []
    for index in range(len(role_array)):
        if index < len(ROLE_GROUP) and role_array[index]:
            roles.append(ROLE_GROUP[index])
    return roles

def encrypt_passwd(pad):
    # return pad
    if not isinstance(pad, str):
        pad = str(pad)
    return md5(pad + "gezlive").hexdigest()

# def test():
#     from usermanager.models import CustomerAccount
#     accounts = CustomerAccount.objects.all()
#     for account in accounts:
#         password = account.password
#         account.password = encrypt_passwd(password)
#         account.save()

# def save_file():
#     from usermanager.models import CustomerAccount
#     import json
#     accounts = CustomerAccount.objects.all()
#     data = []
#     for account in accounts:
#         data.append({"id": account.id, "username": account.username, "password": account.password})
#     fd = open("oldkey.txt", "w")
#     fd.write(json.dumps(data))
#     fd.close()

if __name__ == "__main__":
    print decode_role(1)
    print encode_role([1, 2, 3])
