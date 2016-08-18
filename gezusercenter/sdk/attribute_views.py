# -- encoding: utf-8 --
try:
    import simplejson as json
except:
    import json
from rest_framework.decorators import detail_route
from rest_framework import viewsets
from products.models import ProductCategory, ProductCategoryAttribute, ProductCategoryAttributeValue
from rest_framework import status
from rest_framework.response import Response
from django.core.cache import cache
from pre_check import PermissionCheck
from toolkit.mylogger import Logger

class AttributeViewSet(PermissionCheck, viewsets.ViewSet):
    """
        获取属性、属性值
    """

    def create(self, request):
        """
        :param request:
        :return:
        """
        cid = request.POST.get("cid", None)
        return self.query_data(cid)

    def list(self, request):
        """
        :param request:
        :return:
        """
        cid = request.GET.get("cid", None)
        return self.query_data(cid)

    def query_data(self, cid):
        """
        :param cid:
        :return:
        """
        Logger.debug("get cmd get_attribute.")
        data = cache.get("product_attr_list_{}".format(cid))
        if data:
            Logger.debug("get_attribute query data from cache.")
            return Response(data, status=status.HTTP_200_OK)
        if cid:
            category = ProductCategory.objects.prefetch_related("attributes__values").filter(pk=cid)
            if not category.exists():
                return Response(json.dumps({"code": 1, "msg": "类别id未知！", "content": ""}),
                                status=status.HTTP_404_NOT_FOUND)
            else:
                category = category[0]
            attrs = category.attributes.filter(active=1)
            product_attr_list = {"id": category.id, "name": category.name, "step": category.step}
        else:
            attrs = ProductCategoryAttribute.objects.prefetch_related("values").filter(active=1)
            product_attr_list = {"id": None, "name": None, "step": None}
        attr_list = []
        for attr in attrs:
            attr_dic = {}
            attr_dic['id'] = attr.id
            if attr.category:
                attr_dic['cid'] = attr.category.id
            else:
                attr_dic["cid"] = None
            attr_dic['name'] = attr.name
            temp = []
            for value in attr.values.filter(active=1):
                temp.append({
                    "id": value.id,
                    "value": value.value
                })
            attr_dic['values'] = temp
            attr_list.append(attr_dic)
        product_attr_list["attr"] = attr_list
        response_data = json.dumps({"code": 0, "msg": "查询数据成功！", "content": product_attr_list})
        cache.set("product_attr_list_{}".format(cid), response_data, timeout=60)
        Logger.debug("get_attribute query data from databse successfl.")
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        ProductCategoryAttribute.objects.filter(pk=pk).update(
            active=False)
        ProductCategoryAttributeValue.objects.filter(attribute_id=pk).update(active=False)
        return Response({'success': 1}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def default_values(self, request, pk=None):
        values = json.loads(ProductCategoryAttribute.objects.get(pk=pk).value)
        return Response(values, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        attribute = ProductCategoryAttribute.objects.get(pk=pk)
        index = int(request.POST.get('index', 0))
        text = request.POST.get('text').strip()
        values = json.loads(attribute.value)
        pre_text = ''
        if len(values) <= index:
            values.append(text)
        else:
            pre_text = values[index]
            values[index] = text
        attribute.value = json.dumps(values)
        attribute.save()
        attribute.values.filter(value=pre_text).update(value=text)
        return Response({'success': 1}, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def delete_default_value(self, request, pk=None):
        attribute = ProductCategoryAttribute.objects.get(pk=pk)
        index = int(request.POST.get('index', 0))
        values = json.loads(attribute.value)
        if index < len(values):
            pre_text = values[index]
            values.remove(pre_text)
            attribute.value = json.dumps(values)
            attribute.save()
            attribute.values.filter(value=pre_text).delete()
        return Response({'success': 1}, status=status.HTTP_200_OK)
