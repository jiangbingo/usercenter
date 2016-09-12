# -- encoding: utf-8 --
__author__ = 'PD-002'

try:
    import simplejson as json
except:
    import json
import base64
import os

import rsa

class RsaServer:
    """
        rsa校验服务端校验方式
    """
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pubkey.txt")

    @classmethod
    def check(cls, sec_data, sign):
        pubkey = cls._loadkey(cls.key_path)
        try:
            my_sign = base64.b64decode(sign)
            if rsa.verify(sec_data, my_sign, pubkey):
                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _loadkey(filename):
        with open(filename) as fd:
            key_data = fd.read()
        return rsa.PublicKey.load_pkcs1(key_data)


class RasClient:
    """
        rsa校验客户端数据处理方式
    """
    def __init__(self, data):
        self.data = data

    def create(self):
        my_sign = self._sign(self.data)
        self.data["sign_type"] = "RSA-1"
        self.data["sign"] = my_sign
        return self.data

    def _sign(self, data):
        privkey = self._loadkey('privkey.txt')
        my_sign = rsa.sign(data["sec_data"], privkey, "SHA-1")
        return base64.b64encode(my_sign)

    @staticmethod
    def _loadkey(filename):
        with open(filename) as fd:
            key_data = fd.read()
        return rsa.PrivateKey.load_pkcs1(key_data)

class RsaBulid:
    """
        生成rsa秘钥
    """
    def __init__(self):
        self.keysize = 512

    def build(self):
        (pubkey, privkey) = rsa.newkeys(self.keysize)
        self.save_to_file("pubkey.txt", pubkey)
        self.save_to_file("privkey.txt", privkey)

    @staticmethod
    def save_to_file(filename, content, format_name="PEM"):
        content = content.save_pkcs1(format=format_name)
        with open(filename, "w+") as fd:
            fd.write(content)

if __name__ == "__main__":
    # RsaBulid().build()
    # data = {"aa": 12, "bb": "", "cc": "dd"}
    data = {"sec_data": "7gLdKx8nUnLn1Q2sUiSwAl5KxZ6Ys2iKk8lJdVkD9f1WmIj0vSp8BeK6mXyVyZbGc0eUtF9CdJuCaRtYfAsFqBjJfAq8YwZfTxRmSs7AxQlBlMyVkXiV4VoEeEfHtPhRh0rFq4J6j5hE7uRt0000000000000000"}
    create_data = RasClient(data).create()
    print "sign", create_data["sign"]
    print RsaServer.check(data["sec_data"], create_data["sign"])
    # print "check: ", RsaServer.check(create_data)
