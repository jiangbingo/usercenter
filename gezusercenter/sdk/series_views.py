# -*- encoding: utf-8 -*-
from django.core.cache import cache
from products.models import ProductCategoryAttributeValue
from products.product_utils import *
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from toolkit.mylogger import Logger

from pre_check import PermissionCheck


class SeriesViewSet(PermissionCheck, viewsets.ViewSet):
    def list(self, request):
        mid = request.GET.get("mid", None)
        return self.query_data(mid)

    def create(self, request):
        mid = request.POST.get("mid", None)
        return self.query_data(mid)

    def query_data(self, mid):
        Logger.debug("get cmd get_series.")
        data = cache.get("brand_list_{}".format(mid))
        if data:
            Logger.debug("get_series query data from cache.")
            return Response(data, status=status.HTTP_200_OK)
        brands = []
        if mid:
            mid = int(mid)
            manu = Manufactor.objects.filter(id=mid).prefetch_related("brands__series").first()
            if manu is None:
                return Response(json.dumps({"code": 1, "msg": "can not find the manufactory whith id={}".format(mid),
                                            "content": ""}), status=status.HTTP_404_NOT_FOUND)
            else:
                brands = manu.brands.filter(active=1)
        else:
            brands = ProductBrand.objects.prefetch_related("series").select_related("manufactory").filter(active=1)
        brand_list = []
        for brand in brands:
            bd = {}
            bd["name"] = brand.name
            bd["id"] = brand.id
            bd["mid"] = [brand.manufactory.id]
            se = []
            for series in brand.series.filter(active=1):
                se.append({"name": series.name, "id": series.id})
            bd["series"] = se
            brand_list.append(bd)
        response_data = json.dumps({"code": 0, "msg": "查询数据成功！", "content": brand_list})
        cache.set("brand_list_{}".format(mid), response_data, timeout=2)
        Logger.debug("get_series query data from database successful.")
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        ProductBrandSeries.objects.filter(pk=pk).update(active=False)
        return Response({'success': 1}, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        name = request.POST.get('name').strip()
        if name == '':
            return Response({'success': 0, 'message': '系列名不能为空'}, status=status.HTTP_200_OK)
        ProductBrandSeries.objects.filter(pk=pk).update(name=name)
        return Response({'success': 1}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def batch_delete(self, request):
        ids = request.POST.get('ids').split(',')
        ProductBrandSeries.objects.filter(pk__in=ids).update(active=False)
        return Response({'success': 1}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def attribute_values(self, request, pk=None):
        category_id = request.GET.get('category_id')
        attributes = get_category_attribute_values(category_id, pk)
        return Response(attributes, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def update_attribute_values(self, request, pk):
        attribute_ids = request.POST.getlist('ids[]')
        attribute_values = request.POST.getlist('values[]')
        attribute_searchable = request.POST.getlist('searchables[]')
        if not len(attribute_ids) == len(attribute_values) == len(
                attribute_searchable):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        for index in range(len(attribute_ids)):
            id = attribute_ids[index]
            value = attribute_values[index]
            searchable = int(attribute_searchable[index])
            attribute_value, flag = ProductCategoryAttributeValue.objects.get_or_create(
                attribute_id=id, series_id=pk)
            attribute_value.value = value
            attribute_value.searchable = searchable == 1
            attribute_value.save()
        return Response({'success': 1}, status=status.HTTP_200_OK)
