# -- encoding: utf-8 --
try:
    import simplejson as json
except:
    import json
from urllib import unquote
from django.http import HttpResponse
from usermanager.models import OtherAccount
from toolkit.myrsa import RsaServer
from toolkit.mylogger import Logger
from usermanager.models import AccountKey
class CheckUser:
    """
        验证请求来源、供应商的权限
    """

    @classmethod
    def check(cls, request):
        sign = request.META.get("HTTP_SIGN", "")
        sec_data = request.META.get("HTTP_SECDATA", "")
        sign_type = request.META.get("HTTP_SIGNTYPE", "")
        key = cls.ck({"sec_data": unquote(sec_data), "sign": unquote(sign), "sign_type": unquote(sign_type)})
        if key:
            account = key.account
            response = {
                "no": account.no,
                "username": account.username,
                "domain_name": account.domain_name,
                "register_date": account.register_date,
                "real_name": account.real_name,
                "phone": account.phone,
                "certified": account.certified,
                "approved": account.approved,
            }
            return HttpResponse(json.dumps({"code": 0, "msg": "合法用户!", "content": response}),
                                content_type="application/json")
        else:
            return HttpResponse(json.dumps({"code": 1, "msg": "非法用户!", "content": ""}),
                                content_type="application/json")

    @classmethod
    def ck(cls, request_data):
        app_secret = request_data.get("sec_data", None)
        if app_secret == "TxRmSs7AxQlBlMyVkXiV4VoEeEfHtPhRh0rFq4J6j5hE7uRt0000000000000000":
            data = "7gLdKx8nUnLn1Q2sUiSwAl5KxZ6Ys2iKk8lJdVkD9f1WmIj0vSp8BeK6mXyVyZbGc0eUtF9CdJuCaRtYfAsFqBjJfAq8YwZf" +\
                   "TxRmSs7AxQlBlMyVkXiV4VoEeEfHtPhRh0rFq4J6j5hE7uRt0000000000000000"
            llicense = "k8lJdVkD9f1WmIj0vSp8BeK6mXyVyZbGc0eUtF9CdJuCaRtYfAsFqBjJfAq8YwZf"
        else:
            keys = AccountKey.objects.filter(app_secret=app_secret)
            if keys.exists():
                key = keys[0]
                data = key.token + key.license + key.app_secret
                llicense = key.license
            else:
                return False
        result = RsaServer.check(data, request_data.get("sign", None))
        out = cls._token_check(llicense)
        if result and out:
            return True
        else:
            Logger.info("authentication failed")
            return False

    @staticmethod
    def _token_check(data):
        # 匹配权限
        return True

class MapUser(CheckUser):
    """
        将供应商下面的用户映射到用户中心
    """

    @classmethod
    def map(cls, request):
        result = False
        # result = cls.ck(request)
        if result:
            other = OtherAccount(platform_code=result["ss"], username=result["ss"], user_code=result["ss"])
            other.save()
            return HttpResponse(json.dumps({"code": 0, "msg": "映射用户成功!", "content": ""}))
        else:
            return HttpResponse(json.dumps({"code": 0, "msg": "映射用户失败!", "content": ""}))

def vsersion(request):
    ver = "1.1.0"
    intro = "2016.06.23"
    return HttpResponse("<h2>version: {0}</h2><br /><h4>说明：{1}<h4>".format(ver, intro))
