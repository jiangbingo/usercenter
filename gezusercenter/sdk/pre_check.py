# -*- encoding: utf-8 -*-
__author__ = 'PD-002'

try:
    import simplejson as json
except:
    import json
from urllib import unquote

from authentication.views import CheckUser
from django.http import HttpResponse


class PermissionCheck(object):
    """
        校验每次请求的权限
    """
    def dispatch(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        sign = request.META.get("HTTP_SIGN", "")
        sec_data = request.META.get("HTTP_SECDATA", "")
        sign_type = request.META.get("HTTP_SIGNTYPE", "")
        if not CheckUser.ck({"sec_data": unquote(sec_data), "sign": unquote(sign), "sign_type": unquote(sign_type)}):
            response = {"code": -1, "msg": "权限认证失败", "content":  ""}
            return HttpResponse(json.dumps(json.dumps(response)), content_type="application/json")
        return super(PermissionCheck, self).dispatch(request, *args, **kwargs)
