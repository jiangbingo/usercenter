# coding:utf-8
import json
import time

from django.db.models import Q

from models import ProductCategory, ProductBrand, ProductBrandSeries, ProductCategoryAttribute, Manufactor


class Node(object):
    def __init__(self, _id, pid, obj):
        self.id = _id
        self.pid = pid
        self.obj = obj
        self.child = []
        self.idorder = ""

    def get_pid(self):
        return self.pid

    def get_id(self):
        return self.id

    def get_obj(self):
        return self.obj

    def add_child(self, node):
        self.child.append(node)

    def get_id_order(self):
        self.idorder += "%s" % self.id

        if len(self.child) == 0:
            return self.idorder

        self.idorder += ','

        for node in self.child:
            if node is self.child[-1]:
                self.idorder += node.get_id_order()
                break
            self.idorder += node.get_id_order() + ','
        res = self.idorder
        self.idorder = ""
        return res


class Sortnode(object):
    def __init__(self):
        pass

    def get_sorted_node(self, obj):
        nodelist = {}
        res = []
        for node in obj:
            nodelist[node.id] = Node(node.id, node.parent_id, node)
        root = Node(-1, 0, "")
        for node in nodelist.itervalues():
            if node.get_pid() == 0:
                root.add_child(node)
            else:
                nodelist[node.get_pid()].add_child(node)

        order = root.get_id_order().split(",")[1:]
        for elem in order:
            res.append(nodelist[int(elem)].get_obj())
        return res


class listJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, list):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def get_time(t):
    return time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(t))


def get_time_stamp_min(t):
    t = "%s 00:00:00" % t
    t = time.strptime(t, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(t))


def get_time_stamp_max(t):
    t = "%s 23:59:59" % t
    t = time.strptime(t, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(t))


def change_style(content, kw):
    return content.replace(kw, '<span style="background:pink">%s</span>' % kw)


TIME_MAX = 2000000000
TIME_MIN = 1000000000


def get_category(c3_id):
    try:
        c3 = ProductCategory.objects.select_related('parent_category',
                                                    'parent_category__parent_category').get(
            id=c3_id)
        c3_name = c3.name
        c2 = c3.parent_category
        c2_name = c2.name
        c1 = c2.parent_category
        c1_name = c1.name
        return c1_name + '/' + c2_name + '/' + c3_name
    except Exception as e:
        print e.message
        return ''


def get_categories():
    res = []
    for category in ProductCategory.objects.filter(active=True):
        res.append({
            "id": category.id,
            "name": category.name,
            "pid": category.parent_category_id or 0,
            'level': category.step
        })
    return res


def get_sub_categories(category_id):
    categories = ProductCategory.objects.filter(
        parent_category=category_id, active=True)
    res = []
    for c in categories:
        c_dict = {
            "id": c.id,
            "name": c.name,
        }
        res.append(c_dict)
    return res


def get_category_manufactors(category_id):
    manufactors = Manufactor.objects.filter(categories=category_id, active=True)
    res = []
    for comp in manufactors:
        res.append({'id': comp.id, 'name': comp.name})
    return res


def get_manufactor_brands(category_id=None, manufactor_id=None):
    select_q = Q()
    if category_id and not manufactor_id:
        select_q = Q(categories=category_id, active=True)
    if manufactor_id and not category_id:
        select_q = Q(manufactors=manufactor_id, active=True)
    if category_id and manufactor_id:
        select_q = Q(categories=category_id, manufactors=manufactor_id, active=True)
    brands = ProductBrand.objects.filter(select_q)
    res = []
    for brand in brands:
        res.append({'id': brand.id, 'name': brand.name})
    return res


def get_brand_series(brand_id):
    series = ProductBrandSeries.objects.filter(brand=brand_id,active=True)
    res = []
    for se in series:
        res.append({'id': se.id, 'name': se.name})
    return res


def get_category_attributes(category_id):
    attributes = ProductCategoryAttribute.objects.filter(category=category_id,active=True)
    result = []
    for attr in attributes:
        result.append({'id': attr.id, 'name': attr.name,
                       'values': json.loads(attr.value)})
    return result


def get_category_attribute_values(category_id, series_id):
    result = []
    attributes = ProductCategoryAttribute.objects.filter(
        category=category_id,active=True)
    for attr in attributes:
        values = attr.values.filter(series=series_id, active=True)
        searchable = -1
        value = ''
        if values.exists():
            value = values[0].value
            searchable = values[0].searchable and 1 or 0
        result.append({'id': attr.id, 'name': attr.name,
                       'values': json.loads(attr.value), 'value': value,
                       'searchable': searchable})
    return result
