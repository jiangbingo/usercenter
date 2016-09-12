#!-*-encoding: utf-8 -*-
__author__ = 'PD-002'

from django.db.models import Q
from usermanager.user_views import get_request_data, my_response

from .models import Province, City, Area


class Location:
    """
        获取省市区位置信息
    """
    @classmethod
    def get(cls, request):
        """
        :param request:
        :return:
        """
        request_data = get_request_data(request)
        callback = request_data.get("callback", "")
        province = request_data.get("province", "")
        city = request_data.get("city", "")
        area = request_data.get("area", "")
        if province != "":
            if province.isdigit():
                provs = Province.objects.filter(id=province).prefetch_related("cities__areas")
            else:
                provs = Province.objects.filter(Q(name=province) | Q(fullname=province)
                                                ).prefetch_related("cities__areas")
            if provs.exists():
                content = cls.get_provinces(provs)
            else:
                content = []
        elif city != "":
            if city.isdigit():
                cities = City.objects.filter(id=city).prefetch_related("areas")
            else:
                cities = City.objects.filter(Q(name=city) | Q(fullname=city)).prefetch_related("areas")
            if cities.exists():
                content = cls.get_cities(cities)
            else:
                content = []
        elif area != "":
            if area.isdigit():
                areas = Area.objects.filter(id=area)
            else:
                areas = Area.objects.filter(Q(name=area) | Q(fullname=area))
            if areas.exists():
                content = cls.get_area(areas)
            else:
                content = []
        else:
            content = cls.get_provinces(Province.objects.all().prefetch_related("cities__areas"))
        return my_response({"code": 0, "msg": "数据查询成功", "content": content}, callback)

    @classmethod
    def get_provinces(cls, provs):
        prov_list = []
        for pro in provs:
            prov_data = {"id": pro.id, "name": pro.name, "fullname": pro.fullname, "area_code": pro.area_code,
                         "pinyin": pro.pinyin, "location_lat": pro.location_lat.to_eng_string(),
                         "location_lng": pro.location_lng.to_eng_string()}
            if hasattr(pro, "cities"):
                prov_data["cities"] = cls.get_cities(pro.cities.all())
            else:
                prov_data["cities"] = []
            prov_list.append(prov_data)
        return prov_list

    @classmethod
    def get_cities(cls, cities):
        city_list = []
        for city in cities:
            city_data = {"id": city.id, "name": city.name, "fullname": city.fullname,
                         "area_code": city.area_code, "pinyin": city.pinyin,
                         "location_lat": city.location_lat.to_eng_string(),
                         "location_lng": city.location_lng.to_eng_string(),
                         "post_code": city.post_code, "phone_code": city.phone_code}
            if hasattr(city, "areas"):
                city_data["areas"] = cls.get_areas(city.areas.all())
            else:
                city_data["areas"] = []
            city_list.append(city_data)
        return city_list

    @staticmethod
    def get_areas(areas):
        area_list = []
        for area in areas:
            area_data = {"id": area.id, "fullname": area.fullname, "area_code": area.area_code,
                         "location_lat": area.location_lat.to_eng_string(),
                         "location_lng": area.location_lng.to_eng_string()}
            area_list.append(area_data)
        return area_list
