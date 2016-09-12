# -*- encoding:utf-8 -*-
__author__ = 'PD-002'
try:
    import simplejson as json
except:
    import json
from django.core.cache import cache
from products.models import ModelAttribute
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from toolkit.mylogger import Logger

from pre_check import PermissionCheck


class ModelAttributeViewSet(PermissionCheck, viewsets.ViewSet):
    """
        获取模型属性接口
    """
    cache_name = "modelattribute"
    cache_timeout = 60

    def create(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("cmd is get model attribute, method is post.")
        response_data = self.query_data()
        return Response(json.dumps(response_data), status.HTTP_200_OK)

    def list(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("cmd is get model attribute, method is get.")
        response_data = self.query_data()
        return Response(json.dumps(response_data), status.HTTP_200_OK)

    def query_data(self):
        """
        :return:
        """
        cache_data = cache.get(self.cache_name)
        if cache_data is not None:
            Logger.debug("query model attribute from cache.")
            return {"code": 0, "msg": "query model attribute successful.", "content": cache_data}
        name_list = ["lay_status", "is_platform", "is_hardness", "furn_set"]
        response_data = []
        model_attr = ModelAttribute.objects.all().first()
        if model_attr is None:
            Logger.info("query model attribute is null.")
            return {"code": 1, "msg": "model attrbute is null.", "content": ""}
        for name in name_list:
            data = json.loads(getattr(model_attr, name))
            attr_data = {"key": name, "name": data["name"], "choice": data["value"]}
            response_data.append(attr_data)
            # response_data[data["name"]] = data["value"]
        other_args = json.loads(model_attr.other_args)
        if len(other_args) > 0 and isinstance(other_args, list):
            args_data = {"key": "other_args", "name": "其它参数", "choice": []}
            for arg in other_args:
                args_data["choice"].append({"name": arg["name"], "choice": arg["value"]})
            response_data.append(args_data)
        cache.set(self.cache_name, response_data, timeout=self.cache_timeout)
        return {"code": 0, "msg": "query model attribute successful.", "content": response_data}
