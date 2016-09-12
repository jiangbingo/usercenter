# -*- encoding: utf-8 -*-
try:
    import simplejson as json
except:
    import json
import datetime

from braces.views import LoginRequiredMixin
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from product_utils import *
from .models import Product, CategoryManufactor, ProductModelFiles, \
    ProductModelPreviews

# from gezbackend.utils import *

import xlrd
from xlsxwriter.workbook import Workbook
import StringIO


# Create your views here.

class ProductView(LoginRequiredMixin, TemplateView):
    template_name = "products/_product.html"

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)
        context['products'] = self.products
        context['cur_page'] = self.page_id
        context['total_page'] = self.pages
        context['next'] = self.next_page
        context['url'] = self.url
        context['urls'] = json.dumps(self.url)
        context["category"] = json.dumps(get_categories())
        return context

    def get(self, request, *args, **kwargs):
        self.type = int(request.GET.get('type', 0))
        if self.type == 0:
            self.template_name = "products/_product.html"
        else:
            self.template_name = "products/_model.html"
        self.page_id = int(request.GET.get('page_id', 1))

        self.kw = request.GET.get('kw', '')
        self.pn = request.GET.get('pn', '')
        self.c1 = int(request.GET.get('c1', 0))
        self.c2 = int(request.GET.get('c2', 0))
        self.c3 = int(request.GET.get('c3', 0))
        self.com = request.GET.get('c', '')
        self.b = request.GET.get('b', '')
        self.s = request.GET.get('s', '')
        self.order = request.GET.get('order', '')
        self.desc = int(request.GET.get('desc', '0'))
        df = request.GET.get('df', '')
        dt = request.GET.get('dt', '')
        ct1 = get_time_stamp_min(df) if df else 0
        ct2 = get_time_stamp_max(dt) if dt else 0
        self.df = min(ct1, ct2)
        self.dt = max(ct1, ct2)
        self.url = 'type=%s&kw=%s&pn=%s&c1=%s&c2=%s&c3=%s&c=%s&b=%s&s=%s&df=%s&dt=%s&order=%s&desc=%s' % (
            self.type,
            self.kw, self.pn, self.c1, self.c2, self.c3, self.com, self.b,
            self.s,
            df, dt, self.order, self.desc)
        print self.url
        kw_q = Q()
        if self.kw:
            kw_q = Q(name__icontains=self.kw) | Q(
                product_no__icontains=self.kw) | Q(
                category__parent_category__parent_category__name__icontains=self.kw) | Q(
                category__parent_category__name__icontains=self.kw) | Q(
                category__name__icontains=self.kw) | Q(
                manufactor__name__icontains=self.kw) | Q(
                brand__name__icontains=self.kw) | Q(
                series__name__icontains=self.kw)

        pn_q = Q()
        if self.pn:
            pn_q = Q(product_no__icontains=self.pn)
        categroy_q = Q()
        if self.c1:
            categroy_q = Q(category__parent_category__parent_category=self.c1)
            if self.c2:
                categroy_q = Q(category__parent_category=self.c2)
                if self.c3:
                    categroy_q = Q(category=self.c3)
        com_q = Q()
        if self.com:
            com_q = Q(manufactor__name__icontains=self.com)
        b_q = Q()
        if self.b:
            b_q = Q(brand__name__icontains=self.b)
        s_q = Q()
        if self.s:
            s_q = Q(series__name__icontains=self.b)
        ct_q = Q()
        if ct1 or ct2:
            ct_q = Q(create_time__gt=self.df, create_time__lt=self.dt)
        select_q = Q(type=self.type, active=1)

        products = Product.objects.select_related('brand', 'series',
                                                  'manufactor',
                                                  'category',
                                                  'category__parent_category',
                                                  'category__parent_category__parent_category').filter(
            kw_q, com_q, b_q, pn_q, categroy_q, s_q,
            ct_q, select_q).order_by(
            '-id')
        if self.order == 'n':
            products = products.extra(select={
                'gbk_title': 'convert(`products_product`.`name` using gbk)'}).order_by(
                '%sgbk_title' % (self.desc == 0 and '-' or ''))
        elif self.order == 'pn':
            products = products.extra(select={
                'gbk_title': 'convert(`products_product`.`product_no` using gbk)'}).order_by(
                '%sgbk_title' % (self.desc == 0 and '-' or ''))
        elif self.order == 'c1':
            products = products.order_by(
                '%scategory__parent_category__parent_category__name' % (
                    self.desc == 0 and '-' or ''))
        elif self.order == 'c2':
            products = products.extra(select={
                'gbk_title': 'convert(`products_productcategory`.`name` using gbk)'}).order_by(
                '%sgbk_title' % (self.desc == 0 and '-' or ''))
        elif self.order == 'c3':
            products = products.order_by(
                '%scategory__parent_category__name' % (
                    self.desc == 0 and '-' or ''))
        elif self.order == 'c':
            products = products.extra(select={
                'gbk_title': 'convert(`customers_manufactor`.`name` using gbk)'}).order_by(
                '%sgbk_title' % (self.desc == 0 and '-' or ''))
        elif self.order == 'b':
            products = products.extra(select={
                'gbk_title': 'convert(`products_productbrand`.`name` using gbk)'}).order_by(
                '%sgbk_title' % (self.desc == 0 and '-' or ''))
        elif self.order == 's':
            products = products.extra(select={
                'gbk_title': 'convert(`products_productbrandseries`.`name` using gbk)'}).order_by(
                '%sgbk_title' % (self.desc == 0 and '-' or ''))
        elif self.order == 'd':
            products = products.order_by(
                '%screate_time' % (self.desc == 0 and '-' or ''))
        # print order_key

        self.products = []

        per_page = 15

        try:
            p = Paginator(products, per_page)
            self.page = p.page(self.page_id)
            self.pages = p.num_pages
            try:
                self.next_page = Paginator(products, per_page).page(
                    self.page_id + 1).has_next()
            except:
                self.next_page = False
            for product in self.page.object_list:
                brand_name = product.brand and product.brand.name or 'N/A'
                series_name = product.series and product.series.name or 'N/A'
                manufactor_name = product.manufactor and product.manufactor.name or 'N/A'
                c1 = 'N/A'
                c2 = 'N/A'
                c3 = 'N/A'
                if product.category:
                    c3 = product.category.name
                    if product.category.parent_category:
                        c2 = product.category.parent_category.name
                        if product.category.parent_category.parent_category:
                            c1 = product.category.parent_category.parent_category.name
                # cate_obj = ProductCategory.objects.get(id=product.category)
                style = 'N/A'  # ProductCategoryAttribute.objects.get(status=1, category_id=cate_obj, name=u'所属风格').value
                ctime = get_time(product.create_time)
                utime = get_time(product.update_time)
                charlet = ""
                charlet = product.chartlet_path
                self.products.append({
                    "id": product.id if not self.kw else change_style(
                        str(product.id), self.kw.strip()),
                    "name": product.name if not self.kw else change_style(
                        product.name, self.kw.strip()),
                    "product_no": product.product_no if not self.kw else change_style(
                        product.product_no,
                        self.kw.strip()),
                    "brand": brand_name if not self.kw else change_style(
                        brand_name, self.kw.strip()),
                    "series": series_name if not self.kw else change_style(
                        series_name, self.kw.strip()),
                    "c1": c1 if not self.kw else change_style(c1,
                                                              self.kw.strip()),
                    "c2": c2 if not self.kw else change_style(c2,
                                                              self.kw.strip()),
                    "c3": c3 if not self.kw else change_style(c3,
                                                              self.kw.strip()),
                    "manufactor": manufactor_name if not self.kw else change_style(
                        manufactor_name, self.kw.strip()),
                    "style": style if not self.kw else change_style(style,
                                                                    self.kw.strip()),
                    "create_time": ctime if not self.kw else change_style(ctime,
                                                                          self.kw.strip()),
                    "update_time": utime if not self.kw else change_style(utime,
                                                                          self.kw.strip()),
                    "charlet": charlet,
                    "status": product.status,
                    "status_string": product.status and '启用' or '禁用',
                })
                # self.products.reverse()
        except Exception as e:
            print e.message
            self.page = 0
            self.pages = 0
            self.next_page = False
        return super(ProductView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        return HttpResponse(json.dumps({"result": 0, "msg": "action success", "data": ""}), content_type="application/json", status=200)


def upload_product_file(request):
    product_id = request.POST.get('product_id')
    files = request.FILES.getlist('file')
    if len(files) > 0:
        file_name = files[0].name
        model_file = ProductModelFiles()
        model_file.name = file_name
        model_file.file.save(file_name, files[0])
        model_file.product_id = product_id
        model_file.save()
    return HttpResponse(json.dumps(
        {"success": 1, "id": model_file.id, "name": model_file.name,
         "url": model_file.file.url}))


def upload_product_preview(request):
    product_id = request.POST.get('product_id')
    files = request.FILES.getlist('file')
    if len(files) > 0:
        file_name = files[0].name
        model_preview = ProductModelPreviews()
        model_preview.name = file_name
        model_preview.file.save(file_name, files[0])
        model_preview.product_id = product_id
        model_preview.save()
    return HttpResponse(json.dumps(
        {"success": 1, "id": model_preview.id, "name": model_preview.name,
         "url": model_preview.file.url}))


class CategoryView(LoginRequiredMixin, TemplateView):
    template_name = "products/_category.html"

    def get(self, request, *args, **kwargs):
        self.categories = get_categories()
        return super(CategoryView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['categories'] = self.categories
        return context


def import_xls(request):
    if request.method == 'GET':
        return render(request, 'products/upload.html')
    else:
        cache.set('category', [])
        xls_file = request.FILES.get('file')
        data = xlrd.open_workbook(file_contents=xls_file.read())
        table = data.sheets()[0]
        row_count = table.nrows
        cell_count = table.ncols
        print row_count, cell_count
        first_category = ''
        second_category = ''
        third_category = ''
        manufactor_name = ''
        brand_name = ''
        series_name = ''
        datas_array = {}
        category_array = []
        manufactor_array = []
        brand_array = []
        series_array = []
        for row_no in range(1, row_count):
            cells = table.row_values(row_no)
            if cells:
                if cells[0].strip() != '':
                    first_category = cells[0].strip()
                if cells[1].strip() != '':
                    second_category = cells[1].strip()
                if cells[2].strip() != '':
                    third_category = cells[2].strip()
                if cells[3].strip() != '':
                    manufactor_name = cells[3].strip()
                if cells[4].strip() != '':
                    brand_name = cells[4].strip()
                if cells[5].strip() != '':
                    series_name = cells[5].strip()
                if first_category == '':
                    continue
                if not datas_array.get(first_category):
                    datas_array[first_category] = {}
                if not first_category in category_array:
                    category_array.append(first_category)
                if not datas_array[first_category].get(second_category):
                    datas_array[first_category][second_category] = {}
                if not second_category in category_array:
                    category_array.append(second_category)
                if not datas_array[first_category][second_category].get(
                        third_category):
                    datas_array[first_category][second_category][
                        third_category] = []
                if not third_category in category_array:
                    category_array.append(third_category)
                if not (manufactor_name, brand_name, series_name) in \
                        datas_array[first_category][second_category][
                            third_category]:
                    datas_array[first_category][second_category][
                        third_category].append(
                        (manufactor_name, brand_name, series_name))
                if not manufactor_name in manufactor_array:
                    manufactor_array.append(manufactor_name)
                if not brand_name in brand_array:
                    brand_array.append(brand_name)
                if not series_name in series_array:
                    series_array.append(series_name)

        max_first_category_no = 1
        max_second_category_no = 1
        max_third_category_no = 1
        max_manufactor_no = 1
        max_brand_no = 1
        max_series_no = 1
        if ProductCategory.objects.filter(step=1).exists():
            max_first_category_no = \
                ProductCategory.objects.filter(step=1).order_by('-no')[
                    0].no + 1
        if ProductCategory.objects.filter(step=2).exists():
            max_second_category_no = \
                ProductCategory.objects.filter(step=2).order_by('-no')[
                    0].no + 1
        if ProductCategory.objects.filter(step=3).exists():
            max_third_category_no = \
                ProductCategory.objects.filter(step=3).order_by('-no')[
                    0].no + 1
        if Manufactor.objects.exists():
            max_manufactor_no = Manufactor.objects.all().order_by('-no')[0].no + 1
        if ProductBrand.objects.exists():
            max_brand_no = ProductBrand.objects.all().order_by('-no')[
                               0].no + 1
        if ProductBrandSeries.objects.exists():
            max_series_no = \
                ProductBrandSeries.objects.all().order_by('-no')[0].no + 1
        exists_catecories = ProductCategory.objects.filter(name__in=category_array)
        exists_manufactors = Manufactor.objects.filter(name__in=manufactor_array)
        exists_brands = ProductBrand.objects.filter(name__in=brand_array)
        exists_series = ProductBrandSeries.objects.filter(name__in=series_array)
        first_categories = {}
        second_categories = {}
        third_categories = {}
        manufactors = {}
        brands = {}
        series = {}
        for category in exists_catecories:
            if category.step == 1:
                first_categories[category.name] = category
            elif category.step == 2:
                second_categories[category.name] = category
            else:
                third_categories[category.name] = category
        for manufactor in exists_manufactors:
            manufactors[manufactor.name] = manufactor
        for brand in exists_brands:
            brands[brand.name] = brand
        for se in exists_series:
            series[se.name] = se
        new_first_categories = []
        new_second_categories = []
        new_third_categories = []
        new_manufactors = []
        new_brands = []
        new_series = []
        for first_category_name in datas_array.keys():
            if not first_categories.get(first_category_name):
                first_category = ProductCategory(
                name=first_category_name, no=max_first_category_no, step=1)
                new_first_categories.append(first_category)
                max_first_category_no += 1
        ProductCategory.objects.bulk_create(new_first_categories)
        for first_category in ProductCategory.objects.filter(name__in=[category.name for category in new_first_categories],step=1):
            first_categories[first_category.name] = first_category
        for first_category_name in datas_array.keys():
            first_category = first_categories[first_category_name]
            for second_category_name in datas_array[first_category_name].keys():
                if not second_categories.get(second_category_name):
                    second_category = ProductCategory(parent_category=first_category,
                        name=second_category_name, no=max_second_category_no, step=2)
                    new_second_categories.append(second_category)
                    max_second_category_no += 1
        ProductCategory.objects.bulk_create(new_second_categories)
        for second_category in ProductCategory.objects.filter(name__in=[category.name for category in new_second_categories],step=2):
            print second_category.id
            second_categories[second_category.name] = second_category
        for first_category_name in datas_array.keys():
            for second_category_name in datas_array[first_category_name].keys():
                second_category = second_categories[second_category_name]
                for third_category_name in datas_array[first_category_name][second_category_name].keys():
                    if not third_categories.get(third_category_name):
                        third_category = ProductCategory(
                            parent_category=second_category,
                            name=third_category_name,
                            no=max_third_category_no, step=3)
                        new_third_categories.append(third_category)
                        max_third_category_no += 1
        ProductCategory.objects.bulk_create(new_third_categories)
        for third_category in ProductCategory.objects.filter(name__in=[category.name for category in new_third_categories],step=3):
            third_categories[third_category.name] = third_category
        for first_category_name in datas_array.keys():
            for second_category_name in datas_array[first_category_name].keys():
                for third_category_name in datas_array[first_category_name][
                    second_category_name].keys():
                    for manufactor_name,brand_name,series_name in datas_array[first_category_name][
                        second_category_name][third_category_name]:
                        print manufactor_name,brand_name,series_name
                        if not manufactors.get(manufactor_name):
                            manufactor = Manufactor(name=manufactor_name,no=max_manufactor_no)
                            max_manufactor_no += 1
                            new_manufactors.append(manufactor)
                        if not brands.get(brand_name):
                            brand = ProductBrand(name=brand_name,no=max_brand_no)
                            max_brand_no += 1
                            new_brands.append(brand)

        Manufactor.objects.bulk_create(new_manufactors)
        ProductBrand.objects.bulk_create(new_brands)

        for manufactor in Manufactor.objects.filter(name__in=[manufactor.name for manufactor in new_manufactors]):
            manufactors[manufactor.name] = manufactor
        for brand in ProductBrand.objects.filter(name__in=[brand.name for brand in new_brands]):
            brands[brand.name] = brand
        exists_category_manufactors = CategoryManufactor.objects.filter(category__in=third_categories.values(),manufactor__in=manufactors.values())
        exists_category_brands = CategoryBrand.objects.filter(category__in=third_categories.values(),brand__in=brands.values())
        exists_manufactor_brands = ManufactorBrand.objects.filter(manufactor__in=manufactors.values(),brand__in=brands.values())
        category_manufactors = {}
        category_brands = {}
        manufactor_brands = {}
        for category_manufactor in exists_category_manufactors:
            category_manufactors[(category_manufactor.category.name,category_manufactor.manufactor.name)] = category_manufactor

        for category_brand in exists_category_brands:
            category_brands[(category_brand.category.name,category_brand.brand.name)] = category_brand
        for manufactor_brand in exists_manufactor_brands:
            manufactor_brands[(manufactor_brand.manufactor.name,manufactor_brand.brand.name)] = manufactor_brand
        new_category_manufactors = []
        new_category_brands = []
        new_manufactor_brands = []
        for first_category_name in datas_array.keys():
            for second_category_name in datas_array[first_category_name].keys():
                for third_category_name in datas_array[first_category_name][
                    second_category_name].keys():
                    category = third_categories[third_category_name]
                    for manufactor_name, brand_name, series_name in \
                    datas_array[first_category_name][
                        second_category_name][third_category_name]:
                        manufactor = manufactors[manufactor_name]
                        if not category_manufactors.get((third_category_name,manufactor_name)):
                            category_manufactor = CategoryManufactor(category=category,manufactor=manufactor)
                            new_category_manufactors.append(category_manufactor)
        for first_category_name in datas_array.keys():
            for second_category_name in datas_array[first_category_name].keys():
                for third_category_name in datas_array[first_category_name][
                    second_category_name].keys():
                    category = third_categories[third_category_name]
                    for manufactor_name, brand_name, series_name in \
                            datas_array[first_category_name][
                                second_category_name][third_category_name]:
                        brand = brands[brand_name]
                        if not category_brands.get((third_category_name,
                                                      brand_name)):
                            category_brand = CategoryBrand(
                                category=category, brand=brand)
                            new_category_brands.append(category_brand)
        for first_category_name in datas_array.keys():
            for second_category_name in datas_array[first_category_name].keys():
                for third_category_name in datas_array[first_category_name][
                    second_category_name].keys():
                    for manufactor_name, brand_name, series_name in \
                            datas_array[first_category_name][
                                second_category_name][third_category_name]:
                        manufactor = manufactors[manufactor_name]
                        brand = brands[brand_name]
                        if not manufactor_brands.get((manufactor_name,
                                                   brand_name)):
                            manufactor_brand = ManufactorBrand(
                                manufactor=manufactor, brand=brand)
                            new_manufactor_brands.append(manufactor_brand)
        CategoryManufactor.objects.bulk_create(new_category_manufactors)
        CategoryBrand.objects.bulk_create(new_category_brands)
        ManufactorBrand.objects.bulk_create(new_manufactor_brands)
        for first_category_name in datas_array.keys():
            for second_category_name in datas_array[first_category_name].keys():
                for third_category_name in datas_array[first_category_name][
                    second_category_name].keys():
                    for manufactor_name, brand_name, series_name in \
                            datas_array[first_category_name][
                                second_category_name][third_category_name]:
                        brand = brands[brand_name]
                        if not series.get(series_name):
                            se = ProductBrandSeries(name=series_name,brand=brand,
                                                    no=max_series_no)
                            max_series_no += 1
                            new_series.append(se)
        ProductBrandSeries.objects.bulk_create(new_series)
        return HttpResponse(json.dumps({'success': 1}))
        # return render(request, 'products/upload.html')


def export_xls(request):
    output = StringIO.StringIO()

    with Workbook(output) as book:
        format = book.add_format()
        format.set_border(1)
        format.set_align('center')
        format.set_valign('vcenter')
        sheet = book.add_worksheet('test')
        sheet.write(0, 0, u'一级分类', format)
        sheet.write(0, 1, u'二级分类', format)
        sheet.write(0, 2, u'三级分类', format)
        sheet.write(0, 3, u'厂家', format)
        sheet.write(0, 4, u'品牌', format)
        sheet.write(0, 5, u'系列', format)

        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 10)

        categories = ProductCategory.objects.filter(step=1)
        row_no = 1
        for category in categories:
            first_row = row_no
            for c2 in category.sub_categories.all():
                second_row = row_no
                for c3 in c2.sub_categories.all():
                    for manufactor in c3.manufactors.all():
                        for brand in c3.brands.filter(manufactors=manufactor):
                            for series in brand.series.all():
                                sheet.write(row_no, 2, c3.name, format)
                                sheet.write(row_no, 3, manufactor.name, format)
                                sheet.write(row_no, 4, brand.name, format)
                                sheet.write(row_no, 5, series.name, format)
                                row_no += 1
                sheet.merge_range(second_row, 1, row_no - 1, 1, c2.name, format)
            sheet.merge_range(first_row, 0, row_no - 1, 0, category.name,
                              format)

            # construct response

    output.seek(0)
    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response[
        'Content-Disposition'] = u"attachment; filename='s%s.xlsx'" % datetime.datetime.now().microsecond

    return response
