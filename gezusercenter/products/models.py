# -*- encoding:utf-8 -*-
try:
    import simplejson as json
except:
    import json
import time

from django.db import models
from toolkit.randomcode import get_random_code
from toolkit.utils import get_resources_path, get_models_path


# 产品数据表
class Product(models.Model):
    TYPE_PRODUCT = 0
    TYPE_MODEL = 1
    TYPE_CHOICES = (
        (TYPE_PRODUCT, '产品'),
        (TYPE_MODEL, '模型'),
    )
    client_product_id = models.IntegerField(default=0, null=False)
    name = models.CharField(max_length=200, default='', null=False)
    category = models.ForeignKey('ProductCategory', related_name='products', default=None, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    brand = models.ForeignKey('ProductBrand', related_name='products', default=None, null=True, blank=True,
                              on_delete=models.SET_NULL)
    series = models.ForeignKey('ProductBrandSeries', related_name='products', default=None, null=True, blank=True,
                               on_delete=models.SET_NULL)
    # 产品价格
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    # 模型默认放置对象(用作默认吸附规则)
    lay_status = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 是否载物台
    is_platform = models.BooleanField(default=False)
    # 是否硬装
    is_hardness = models.BooleanField(default=False)
    # 家具分类打标
    furn_set = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 其他模型属性参数
    other_model_args = models.TextField(default=json.dumps({}))
    # 产品编号
    product_no = models.CharField(max_length=200, default='', null=False)
    attr_val = models.CharField(max_length=100, default='', null=False)
    rule_val = models.CharField(max_length=100, default='', null=False)
    is_ornament = models.IntegerField(default=0, null=False)
    status = models.IntegerField(default=0, null=False)
    # 厂家
    manufactor = models.ForeignKey('Manufactor', related_name='products', default=None, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    # 供应商
    distributors = models.ManyToManyField('usermanager.Distributor', related_name='products',
                                          through='ProductDistributor')
    create_time = models.IntegerField(default=0, null=False)
    update_time = models.IntegerField(default=0, null=False)
    args = models.TextField(default='')
    # 备注
    remark = models.TextField(default='')
    type = models.IntegerField(default=TYPE_PRODUCT, choices=TYPE_CHOICES)
    version_no = models.CharField(max_length=200, default='')
    # 型号
    norms_no = models.CharField(max_length=200, default='', null=False)
    # 材质
    material = models.CharField(max_length=100, default='', null=False)
    # 长
    length = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    # 宽
    width = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    # 高
    height = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    # 工艺
    technics = models.CharField(max_length=100, default='', null=False)
    # 颜色
    color = models.CharField(max_length=10, default='', null=False)
    # 家具分类打标
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s(%s)' % (self.name, self.product_no)

    @property
    def chartlet_path(self):
        path = ''
        if self.previews.exists():
            path = self.previews.all().order_by('-id')[0].file.url
        return path

    @property
    def normal(self):
        vir_exists = False
        obj_exists = False
        for file in self.files.all():
            if file.name.lower().endswith('.vir'):
                vir_exists = True
            elif file.name.lower().endswith('.obj'):
                obj_exists = True
        return vir_exists and obj_exists

    def generate_product_no(self):
        product_no = '%s%s%s%s%s%s%s%s' % (time.strftime('%Y%m%d', time.localtime(self.create_time)),
                                           self.category and self.category.parent_category.parent_category.category_no,
                                           self.category and self.category.parent_category.category_no,
                                           self.category and self.category.category_no,
                                           self.manufactor and self.manufactor.manufactor_no,
                                           self.brand and self.brand.brand_no,
                                           self.series and self.series.series_no,
                                           get_random_code(4))
        self.product_no = product_no
        self.save()
        return product_no

    class Meta:
        db_table = 'products_product'

class ModelAttribute(models.Model):
    # 模型默认放置对象(用作默认吸附规则)
    lay_status = models.TextField(default=json.dumps({}))
    # 是否载物台
    is_platform = models.TextField(default=json.dumps({}))
    # 是否硬装
    is_hardness = models.TextField(default=json.dumps({}))
    # 家具分类打标
    furn_set = models.TextField(default=json.dumps({}))
    other_args = models.TextField(default=json.dumps({}))

    class Meta:
        db_table = 'products_modelattribute'

class ProductDistributor(models.Model):
    product = models.ForeignKey("Product")
    distributor = models.ForeignKey("usermanager.Distributor")
    link_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products_productdistributor'

class ProductAttribute(models.Model):
    product = models.ForeignKey("Product", related_name='attributes', default=None, null=True, blank=True,
                                on_delete=models.SET_NULL)
    attribute = models.ForeignKey('ProductCategoryAttribute', default=None, null=True, blank=True,
                                  on_delete=models.SET_NULL)
    value = models.CharField(max_length=100, default='', null=False)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s %s %s' % (self.product.name, self.attribute.name, self.value)

    class Meta:
        db_table = 'products_productattribute'

class ProductModelZip(models.Model):
    product = models.ForeignKey("Product", related_name='zip_files', default=None, null=True, blank=True,
                                on_delete=models.SET_NULL)
    file = models.FileField(upload_to=get_models_path(), null=True, default=None)
    upload_time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'products_productmodelzip'

class ProductModel(models.Model):
    product = models.ForeignKey("Product", related_name='models', default=None, null=True, blank=True,
                                on_delete=models.SET_NULL)
    # 名称
    name = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 来源
    source = models.CharField(max_length=200, null=True, blank=True, default=None)
    # 规格
    size = models.CharField(max_length=200, null=True, blank=True, default=None)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'products_productmodel'

class ProductModelFiles(models.Model):
    model = models.ForeignKey('ProductModel', related_name='files', default=None, null=True, blank=True,
                              on_delete=models.SET_NULL)
    name = models.CharField(max_length=200, default=None, null=True, blank=True)
    file = models.FileField(upload_to=get_models_path(), null=True, default=None)
    type = models.CharField(max_length=200, null=True, blank=True, default=None)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'products_productmodelfiles'

# 贴图文件
class ProductModelPreviews(models.Model):
    name = models.CharField(max_length=200, default='', null=False)
    product = models.ForeignKey("Product", related_name='previews', default=None, null=True, blank=True,
                                on_delete=models.SET_NULL)
    file = models.FileField(upload_to=get_models_path())
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'products_productmodelpreviews'

# 产品分类数据表
class ProductCategory(models.Model):
    parent_category = models.ForeignKey('ProductCategory', related_name='sub_categories', default=None, null=True,
                                        blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, default='', null=False)
    step = models.IntegerField(default=1, null=False)   #分类目录树所处等级
    no = models.IntegerField(default=0, null=False)
    manufactors = models.ManyToManyField("Manufactor", through='CategoryManufactor', related_name='categories')
    active = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s(%s)' % (self.name, self.category_no)

    @property
    def category_no(self):
        if self.step == 1:
            return 'a%s' % self.no
        elif self.step == 2:
            return 'b%s' % self.no
        else:
            return 'c%s' % self.no

    class Meta:
        db_table = 'products_productcategory'

class CategoryManufactor(models.Model):
    category = models.ForeignKey('ProductCategory')
    manufactor = models.ForeignKey('Manufactor')

    class Meta:
        db_table = 'products_categorymanufactor'

# 产品分类属性关系数据表
class ProductCategoryAttribute(models.Model):
    """
        产品分类属性关系数据表
    """
    STATUS_CHOICES = (
        (0, '未处理'),
        (1, '已处理')
    )
    category = models.ForeignKey("ProductCategory", related_name='attributes', default=None, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, default='', null=False)
    searchable = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    # 来源
    source = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 状态
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    @property
    def value_string(self):
        values = []
        for value in self.values.all():
            if value.active:
                values.append(value.value)
        return ','.join(values)

    @property
    def value_dict(self):
        values = {}
        for value in self.values.all():
            if value.active:
                values.update({value.id: value.value})
        return values

    @property
    def value_array(self):
        values = []
        for value in self.values.all():
            if value.active:
                values.append(value.value)
        return values

    @property
    def status_unicode(self):
        return ProductCategoryAttribute.STATUS_CHOICES[self.status][1]

    class Meta:
        db_table = 'products_productcategoryattribute'

# 产品分类属性数值信息表
class ProductCategoryAttributeValue(models.Model):
    attribute = models.ForeignKey("ProductCategoryAttribute", related_name='values', default=None, null=True,
                                  blank=True, on_delete=models.SET_NULL)
    value = models.CharField(max_length=100, default='', null=False)
    no = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s: %s' % (self.attribute.name, self.value)

    class Meta:
        db_table = 'products_productcategoryattributevalue'

# 客户单位数据表
class Manufactor(models.Model):
    """
        客户单位数据表
    """
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = (
        (GENDER_MALE, '男'),
        (GENDER_FEMALE, '女'),
    )
    # 真实姓名
    real_name = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 真实性别
    gender = models.IntegerField(choices=GENDER_CHOICES, default=GENDER_MALE)
    # 身份证号
    cert_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    company_name = models.CharField(max_length=200, default=None, null=True, blank=True)
    no = models.IntegerField(default=0, null=False)
    other_account = models.OneToOneField('usermanager.OtherAccount', related_name='manufactory',
                                         default=None, null=True, blank=True, on_delete=models.SET_NULL)
    # 拿到代理的经销商
    customers = models.ManyToManyField('usermanager.CustomerAccount', related_name='manufactors',
                                       through='CustomerManufactor')
    # 厂商
    manufacturer = models.OneToOneField('usermanager.CustomerAccount', related_name='manufactory',
                                        default=None, null=True, blank=True,  on_delete=models.SET_NULL)
    # 注册号
    register_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 营业执照
    business_license = models.FileField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 授权
    active = models.BooleanField(default=True)
    # 省
    province = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 市
    city = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 区
    area = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 联系人
    contact = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 联系电话
    contact_no = models.CharField(max_length=200, default=None, null=True, blank=True)
    image = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    key = models.ForeignKey('usermanager.AccountKey', related_name='manufactories', default=None, null=True, blank=True,
                            on_delete=models.SET_NULL)

    def __unicode__(self):
        return '%s(%s)' % (self.name, self.manufactor_no)

    @property
    def manufactor_no(self):
        return 'd%s' % self.no

    class Meta:
        db_table = 'products_manufactor'

class DistributorBrand(models.Model):
    distributor = models.ForeignKey('usermanager.Distributor')
    brand = models.ForeignKey('ProductBrand')

    class Meta:
        db_table = 'products_distributorbrand'

class CustomerManufactor(models.Model):
    customer = models.ForeignKey('usermanager.CustomerAccount')
    manufactor = models.ForeignKey('Manufactor')

    class Meta:
        db_table = 'products_customermanufactor'

# 产品品牌关系数据
class ProductBrand(models.Model):
    """
        产品品牌关系数据
    """
    name = models.CharField(max_length=100, default='', null=False)
    no = models.IntegerField(default=0, null=False)
    active = models.BooleanField(default=True)
    manufactory = models.ForeignKey('Manufactor', related_name='brands', default=None, null=True, blank=True,
                                    on_delete=models.SET_NULL)

    def __unicode__(self):
        return '%s(%s)' % (self.name, self.brand_no)

    @property
    def brand_no(self):
        return 'e%s' % self.no

    class Meta:
        db_table = 'products_productbrand'

# 产品品牌与系列 关系数据表
class ProductBrandSeries(models.Model):
    """
        产品品牌与系列 关系数据表
    """
    brand = models.ForeignKey("ProductBrand", related_name='series', default=None, null=True, blank=True,
                              on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, default='', null=False)
    no = models.IntegerField(default=0, null=False)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s(%s)' % (self.name, self.series_no)

    @property
    def series_no(self):
        return 'f%s' % self.no

    class Meta:
        db_table = 'products_productbrandseries'