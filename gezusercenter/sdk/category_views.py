# -*- encoding: utf-8 -*-
try:
    import simplejson as json
except:
    import json
from django.core.cache import cache
from products.product_utils import *
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from toolkit.mylogger import Logger

from pre_check import PermissionCheck


class CategoryViewSet(PermissionCheck, viewsets.ViewSet):

    def create(self, request):
        return self.get_all_categories(request)

    def list(self, request):
        return self.get_all_categories(request)
        # return Response(json.dumps({"code": 0, "msg": "权限认证成功", "content": get_categories()}),
        #                 status=status.HTTP_200_OK)

    def get_all_categories(self, request):
        Logger.debug("get cmd get_categories.")
        categories = cache.get("get_all_categories")
        if categories:
            Logger.debug("get_categories query data from cache.")
            return Response(categories, status=status.HTTP_200_OK)
        res = []
        for category in ProductCategory.objects.filter(active=True):
            res.append({
                "id": category.id,
                "name": category.name,
                "pid": category.parent_category_id or 0,
                'level': category.step
            })
        if not res:
            return Response(json.dumps({"code": 1, "msg": "category data query failed!", "content": []}))
        response_data = json.dumps({"code": 0, "msg": "category data query successful!", "content": res})
        cache.set("get_all_categories", response_data, timeout=60)
        Logger.debug("get_categories query data from database successful.")
        return Response(response_data, status=status.HTTP_200_OK)

    @list_route(methods=['get', 'post'])
    def search(self, request):
        kw = request.GET.get('kw').strip()
        series = ProductBrandSeries.objects.select_related(
            'brand').prefetch_related('brand__manufactors', 'brand__categories',
                                      'brand__categories__parent_category',
                                      'brand__categories__parent_category__parent_category').filter(
            Q(name=kw) | Q(brand__name=kw) | Q(
                brand__manufactors__name=kw) | Q(
                brand__categories__name=kw) | Q(
                brand__categories__parent_category__name=kw) | Q(
                brand__categories__parent_category__parent_category__name=kw)).order_by(
            'brand__categories__parent_category__parent_category__no',
            'brand__categories__parent_category__no', 'brand__categories__no',
            'brand__manufactors__no', 'brand__no', 'no')
        result = []
        for se in series:
            for c3 in se.brand.categories.all():
                for manufactor in se.brand.manufactors.all():
                    if not (se.active and se.brand.active and manufactor.active and c3.active and c3.parent_category.active and c3.parent_category.parent_category.active):
                        continue
                    result_dict = {
                        'first_category': c3.parent_category.parent_category.name,
                        'second_category': c3.parent_category.name,
                        'third_category': c3.name,
                        'category_id': c3.id, 'series_id': se.id,
                        'manufactor': manufactor.name, 'brand': se.brand.name,
                        'series': se.name}
                    if result_dict['first_category'] == kw or result_dict[
                        'second_category'] == kw or result_dict[
                        'third_category'] == kw or result_dict[
                        'manufactor'] == kw or result_dict['brand'] == kw or result_dict['series'] == kw:
                            result.append(result_dict)
        return Response(
            {'data': result}, status=status.HTTP_200_OK)

    @detail_route(methods=['get', 'post'])
    def sub_categories(self, request, pk):
        return Response(get_sub_categories(pk),
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get', 'post'])
    def manufactors(self, request, pk):
        return Response(get_category_manufactors(pk),
                        status=status.HTTP_200_OK)

    @detail_route()
    def brands(self, request, pk=None):
        manufactor_id = request.GET.get('manufactor_id', 0)
        return Response(get_manufactor_brands(pk, manufactor_id),
                        status=status.HTTP_200_OK)

    @list_route(methods=['get', 'post'])
    def batch_delete(self, request):
        parent_categories = ProductCategory.objects.filter(
            pk__in=request.POST.get('ids').split(','))
        for parent_category in parent_categories:
            if parent_category.sub_categories.exists():
                parent_category.sub_categories.all().update(active=False)
            parent_category.active = False
            parent_category.save()
            parent_category.delete()
        return Response({'success': 1},
                        status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        parent_category = ProductCategory.objects.get(pk=pk)
        if parent_category.sub_categories.exists():
            parent_category.sub_categories.all().update(active=False)
        parent_category.active = False
        parent_category.save()
        return Response({'success': 1},
                        status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        name = request.POST.get('name').strip()
        if name == '':
            return Response(
                {'success': 0, 'message': '分类名不能为空！'},
                status=status.HTTP_200_OK)
        ProductCategory.objects.filter(pk=pk).update(name=name)
        return Response({'success': 1}, status=status.HTTP_200_OK)

    @detail_route()
    def attribute(self, request, pk=None):
        attributes = get_category_attributes(pk)
        return Response(attributes, status=status.HTTP_200_OK)
