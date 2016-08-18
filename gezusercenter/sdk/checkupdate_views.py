# -- encoding: utf-8 --
__author__ = 'PD-002'
try:
    import simplejson as json
except:
    import json
import base64
import time
from datetime import datetime
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from pre_check import PermissionCheck
from products.models import ProductCategory, ProductBrand, ProductCategoryAttribute
from django.utils import timezone
from django.core.cache import cache
from toolkit.mylogger import Logger

class CheckUpdateViewSet(PermissionCheck, viewsets.ViewSet):
    """
        检查数据是否更新
    """
    cache_flag = "category_brand_attr_flag"

    def create(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd checkupdate, method is post.")
        flag = request.POST.get("flag", None)
        response = self.check(flag)
        return Response(json.dumps(response), status.HTTP_200_OK)

    def list(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd checkupdate, method is get.")
        flag = request.GET.get("flag", None)
        response = self.check(flag)
        return Response(json.dumps(response), status.HTTP_200_OK)

    @classmethod
    def check(cls, flag):
        """
        :param flag:
        :return:
        """
        if not flag:
            return {"code": 2, "msg": "入参错误！", "content":  ""}
        try:
            data = json.loads(flag)
        except:
            return {"code": 2, "msg": "入参错误！", "content":  ""}
        old_flag = cache.get(cls.cache_flag)
        if old_flag:
            Logger.debug("checkupdate get flag from cache.")
            return {"code": 0, "msg": "检测更新成功！", "content":  old_flag}
        new_flag = {}
        category = data.get("category", None)
        if category is not None:
            new_flag["category"] = cls.check_category(category)
        brand = data.get("brand")
        if brand is not None:
            new_flag["brand"] = cls.check_brand(brand)
        attr = data.get("attr")
        if attr is not None:
            new_flag["attr"] = cls.check_attr(attr)
        cache.set(cls.cache_flag, new_flag, timeout=80)
        return {"code": 0, "msg": "检测更新成功！", "content":  new_flag}

    @classmethod
    def check_category(cls, category):
        """
        :param category:
        :return:
        """
        start, count = cls._decode_update_flag(category)
        ct = ProductCategory.objects.all().count()
        if ct != int(count):
            count = ct
            Logger.debug("check_category, count is changed.")
        new = ProductCategory.objects.filter(update_time__gt=cls._format_timestamp(start)).first()
        if new:
            start = time.mktime(new.update_time.timetuple())
            Logger.debug("check_category,data is updated.")
        return base64.b64encode("{0}*{1}".format(count, start))

    @classmethod
    def check_brand(cls, brand):
        """
        :param brand:
        :return:
        """
        start, count = cls._decode_update_flag(brand)
        ct = ProductBrand.objects.all().count()
        if ct != int(count):
            count = ct
            Logger.debug("check_brand, count is changed.")
        # new = ProductBrand.objects.filter(update__gt=cls._format_timestamp(start))).first()
        # if new:
        #     start = new.update_time
        #     Logger.debug("check_brand,data is updated.")
        return base64.b64encode("{0}*{1}".format(count, start))

    @classmethod
    def check_attr(cls, attr):
        """
        :param attr:
        :return:
        """
        start, count = cls._decode_update_flag(attr)
        ct = ProductCategoryAttribute.objects.all().count()
        if ct != int(count):
            count = ct
            Logger.debug("check_attr, count is changed.")
        new = ProductCategoryAttribute.objects.filter(update_date__gt=cls._format_timestamp(start)).first()
        if new:
            start = time.mktime(new.update_date.timetuple())
            Logger.debug("check_attr, data is changed.")
        return base64.b64encode("{0}*{1}".format(count, start))

    @staticmethod
    def _decode_update_flag(data):
        """
        :param data:
        :return:
        """
        if data == "":
            count = 0
            # start = time.time()
            start = 0.0
        else:
            count = 0
            start = time.time()
            try:
                category = base64.b64decode(data)
                count, start = category.split("*")
            except Exception, e:
                Logger.error("checkupdate request data b64decode error: {}".format(e))
        return float(start), count

    @staticmethod
    def _format_timestamp(stamp):
        my_time = datetime.fromtimestamp(stamp)
        tzone = timezone.make_aware(my_time, timezone.get_current_timezone())
        return tzone
