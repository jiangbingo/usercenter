# -*- encoding:utf-8 -*-

import datetime
from django.db import models
from toolkit.randomcode import utc2local
from toolkit.utils import get_resources_path, decode_role, encode_role

class CustomerAccount(models.Model):
    SOURCE_MAIN = 0
    SOURCE_DESIGN = 1
    SOURCE_OR = 2
    SOURCE_SHOP = 3
    SOURCE_CHOICES = (
        (0, '官网'),
        (1, '设计师平台'),
        (2, '电商平台'),
        (3, '商铺')
    )
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = (
        (GENDER_MALE, '男'),
        (GENDER_FEMALE, '女'),
    )
    # 流水号
    no = models.IntegerField(default=0)
    # 用户编码
    account_no = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 来源
    source = models.IntegerField(choices=SOURCE_CHOICES, default=SOURCE_MAIN)
    # 用户名
    username = models.CharField(max_length=200, default=None, null=True, blank=True)
    password = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 角色
    role = models.IntegerField(default=0)
    # 状态
    active = models.BooleanField(default=True)
    # 注册日期
    register_date = models.DateTimeField(auto_now_add=True)
    # 手机号码
    phone = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 邮箱
    email = models.EmailField(max_length=200, default=None, null=True, blank=True)
    email_certified = models.BooleanField(default=False)
    # 电话有效性认证
    phone_certified = models.BooleanField(default=False)
    # 认证
    certified = models.BooleanField(default=False)
    # 授权
    approved = models.BooleanField(default=False)
    # 更新时间
    update_time = models.DateTimeField(auto_now=True)
    # 账户下的个人信息
    personal_info = models.OneToOneField('PersonalInfo', related_name='account', default=None, null=True, blank=True,
                                         on_delete=models.SET_NULL)

    def generate_account_no(self):
        source = ''
        if self.source == 0:
            source = 'o'
        elif self.source == 1:
            source = 'o'
        elif self.source == 2:
            source = 'e'
        elif self.source == 3:
            source = 's'
        no = self.no
        for i in range(4 - len('%s' % self.no)):
            no = '0%s' % no
        self.account_no = '%s%s%s' % (
            source, self.register_date.strftime('%Y%m%d'), no)
        self.save()

    @property
    def register_date_format(self):
        return self.register_date and utc2local(self.register_date).strftime('%Y-%m-%d %H:%M:%S') or 'N/A'

    @property
    def get_role(self):
        return decode_role(self.role)

    @property
    def today_max_count(self):
        today = datetime.date.today()
        today_start = datetime.datetime.combine(today, datetime.datetime.min.time())
        today_end = datetime.datetime.combine(today, datetime.datetime.max.time())
        self.no = CustomerAccount.objects.filter(register_date__range=(today_start, today_end)).count() + 1

    class Meta:
        # 指定表名
        db_table = 'customers_customeraccount'

class PersonalInfo(models.Model):
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = (
        (GENDER_MALE, '男'),
        (GENDER_FEMALE, '女'),
    )
    nick_name = models.CharField(max_length=128, default=None, null=True, blank=True)
    # 头像
    avatar = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 真实姓名
    name = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 性别
    gender = models.IntegerField(choices=GENDER_CHOICES, default=GENDER_MALE)
    # 生日
    birth_date = models.DateField(default=None, null=True, blank=True)
    # 身份信息
    cert_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 身份证有效期
    cert_limit_date = models.DateField(default=None, null=True, blank=True)
    # 身份证附件正面
    cert_attachment_front = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 身份证附件背面
    cert_attachment_back = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 更新时间
    update_time = models.DateTimeField(auto_now=True)
    # 认证
    certified = models.BooleanField(default=False)
    # 金币
    gold = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        db_table = 'customers_personalinfo'

class OtherAccount(models.Model):
    """
        第三方用户表，商铺、电商的用户
    """
    platform = models.ForeignKey('CustomerAccount', related_name='other', default=None, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    app_secret = models.CharField(max_length=128, default=None, null=True, blank=True)
    username = models.CharField(max_length=128, default=None, null=True, blank=True)
    # 手机号码
    phone = models.CharField(max_length=50, default=None, null=True, blank=True)
    uid = models.CharField(max_length=200, default=None, null=True, blank=True)
    email = models.EmailField(max_length=200, default=None, null=True, blank=True)
    role = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    personal_info = models.OneToOneField('PersonalInfo', related_name='other_account', default=None, null=True,
                                         blank=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.username

    @property
    def get_role(self):
        return decode_role(self.role)

    def set_role(self, role):
        roles = self.get_role
        roles.append(role)
        self.role = encode_role(roles)
        self.save()

    class Meta:
        # 指定表名
        db_table = 'customers_otheraccount'

class AccountKey(models.Model):
    """
        供应商秘钥表
    """
    # 应用名称
    name = models.CharField(max_length=200, default=None, null=True, blank=True)
    token = models.CharField(max_length=128, unique=True, default='', null=False)
    license = models.CharField(max_length=64, unique=True, default='', null=False)
    app_secret = models.CharField(max_length=64, unique=True, default='', null=False)

    class Meta:
        # 指定表名
        db_table = 'customers_accountkey'

class Group(models.Model):
    name = models.CharField(max_length=200, default=None, null=True, blank=True)
    secret_key = models.CharField(max_length=64, unique=True, default=None, null=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s: %s' % (self.name, self.secret_key)

    class Meta:
        db_table = "customers_group"

class LicenseGroup(models.Model):
    key = models.ForeignKey('AccountKey', related_name='license_groups', default=None, null=True, blank=True,
                            on_delete=models.SET_NULL)
    group = models.ForeignKey('Group', related_name='licenses', default=None, null=True, blank=True,
                              on_delete=models.SET_NULL)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "customers_licensegroup"

class PendingApprove(models.Model):
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = (
        (GENDER_MALE, '男'),
        (GENDER_FEMALE, '女'),
    )
    ROLE_NORMAL = 0
    ROLE_DESIGNER = 1
    ROLE_OR = 2
    ROLE_SHOP = 3
    ROLE_DECORATION = 4
    ROLE_MANUFACTORY = 5
    ROLE_CHOICES = (
        (0, '普通用户'),
        (1, '设计师'),
        (2, '供应商'),
        (3, '供应商'),
        (4, '装修公司'),
        (5, '供应商')
    )

    TYPE_CERTIFY = 0
    TYPE_APPROVE = 1
    TYPE_GRANT = 2
    TYPE_DISTRIBUTOR = 3
    TYPE_BRAND_SERIES = 4
    TYPE_PRODUCT = 5
    TYPE_CHOICES = (
        (TYPE_CERTIFY, '认证'),
        (TYPE_APPROVE, '用户授权'),
        (TYPE_GRANT, '厂家授权'),
        (TYPE_DISTRIBUTOR, '厂家授权'),
        (TYPE_BRAND_SERIES, '品牌系列授权'),
        (TYPE_PRODUCT, '产品授权'),
    )
    account = models.ForeignKey('CustomerAccount', related_name='pending_approves')
    role = models.IntegerField(choices=ROLE_CHOICES, default=ROLE_NORMAL)
    # 公司名称
    company_name = models.CharField(max_length=200, default=None, null=True, blank=True)
    domain = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 应用名称
    domain_name = models.CharField(max_length=200, default=None, null=True, blank=True)
    domain_description = models.CharField(max_length=2000, default=None, null=True, blank=True)
    # 认证还是审核
    type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_CERTIFY)
    approved = models.BooleanField(default=False)
    register_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    cert_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    bank_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    business_license = models.FileField(default=None, null=True, blank=True, upload_to=get_resources_path())
    manufactory = models.CharField(max_length=200, default=None, null=True, blank=True)
    brand = models.CharField(max_length=200, default=None, null=True, blank=True)
    series = models.CharField(max_length=200, default=None, null=True, blank=True)
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
    # 公司形象照片
    image = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 产品编号
    product_no = models.CharField(max_length=500, default=None, null=True, blank=True)
    grant_to = models.ForeignKey('Distributor', related_name='pending_grants',
                                 default=None, null=True, blank=True, on_delete=models.SET_NULL)
    # 真实姓名
    real_name = models.CharField(max_length=200, default=None, null=True,
                                 blank=True)
    # 性别
    gender = models.IntegerField(choices=GENDER_CHOICES, default=GENDER_MALE)
    # 社交帐号
    social_account = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 所在地
    location = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 公司地址
    company_address = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 设计风格
    design_style = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 个人简介
    personal_profile = models.CharField(max_length=500, default=None, null=True, blank=True)
    # 身份证附件正面
    cert_attachment_front = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 身份证附件背面
    cert_attachment_back = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 设计师资格证正面
    designer_cert_front = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 设计师资格证背面
    designer_cert_back = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    create_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s' % self.account.username

    @property
    def role_unicode(self):
        return PendingApprove.ROLE_CHOICES[self.role][1]

    @property
    def create_date_format(self):
        return self.create_date and utc2local(self.create_date).strftime('%Y-%m-%d %H:%M:%S') or 'N/A'

    @property
    def pending_type(self):
        if self.account.certified:
            return ApproveLog.TYPE_APPROVE
        else:
            return ApproveLog.TYPE_CERTIFY

    class Meta:
        db_table = "customers_pendingapprove"

class ApproveLog(models.Model):
    account = models.ForeignKey('CustomerAccount', related_name='approve_logs')
    approve_info = models.ForeignKey('PendingApprove', related_name='approve_log')
    action_date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    message = models.CharField(max_length=2000, default=None, null=True,
                               blank=True)
    action_user = models.CharField(max_length=200, default=None, null=True,
                                   blank=True)

    @property
    def approved_unicode(self):
        if self.approved:
            return '通过'
        else:
            return '拒绝'

    @property
    def action_date_format(self):
        return self.action_date and utc2local(self.action_date).strftime('%Y-%m-%d %H:%M:%S') or 'N/A'

    class Meta:
        db_table = "customers_approvelog"

# 经销商
class Distributor(models.Model):
    """
        供应商
    """
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = (
        (GENDER_MALE, '男'),
        (GENDER_FEMALE, '女'),
    )
    account = models.OneToOneField('CustomerAccount', related_name='distributors',
                                   default=None, null=True, blank=True, on_delete=models.SET_NULL)
    other_account = models.OneToOneField('OtherAccount', related_name='distributor', default=None, null=True,
                                         blank=True, on_delete=models.SET_NULL)
    # 法人姓名
    name = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 法人性别
    gender = models.IntegerField(choices=GENDER_CHOICES, default=GENDER_MALE)
    # 公司形象照片
    image = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 域名
    domain = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 销售地址
    location = models.CharField(blank=True, default=None, max_length=200, null=True)
    # 公司地址
    company_address = models.CharField(blank=True, default=None, max_length=200, null=True)
    # 公司名称
    company_name = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 应用名称
    domain_name = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 描述
    description = models.CharField(max_length=2000, default=None, null=True, blank=True)
    # 注册号
    register_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 身份信息
    cert_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 银行帐号
    bank_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 营业执照
    business_license = models.FileField(default=None, null=True, blank=True,
                                        upload_to=get_resources_path())
    brands = models.ManyToManyField('products.ProductBrand', through='products.DistributorBrand',
                                    related_name='distributors')
    designers = models.ManyToManyField('Designer', related_name='designer_distributors', through='DesignerDistributor')
    key = models.OneToOneField('AccountKey', related_name='distributors', default=None, null=True, blank=True,
                               on_delete=models.SET_NULL)
    # 省
    province = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 市
    city = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 区
    area = models.CharField(max_length=200, default=None, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "customers_distributor"

class Designer(models.Model):
    """
        设计师
    """
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = (
        (GENDER_MALE, '男'),
        (GENDER_FEMALE, '女'),
    )
    account = models.OneToOneField('CustomerAccount', related_name='designer', default=None, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    other_account = models.OneToOneField('OtherAccount', related_name='designer', default=None, null=True, blank=True,
                                         on_delete=models.SET_NULL)
    # 真实姓名
    real_name = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 真实性别
    gender = models.IntegerField(choices=GENDER_CHOICES, default=GENDER_MALE)
    # 电话
    phone = models.CharField(blank=True, default=None, max_length=20, null=True)
    # 社交帐号
    social_account = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 身份证号
    cert_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 所在地
    location = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 公司名称
    company_name = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 公司地址
    company_address = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 设计风格
    design_style = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 个人简介
    personal_profile = models.CharField(max_length=500, default=None, null=True, blank=True)
    # 身份证附件正面
    cert_attachment_front = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 身份证附件背面
    cert_attachment_back = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 设计师资格证正面
    designer_cert_front = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 设计师资格证背面
    designer_cert_back = models.ImageField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 省
    province = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 市
    city = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 区
    area = models.CharField(max_length=200, default=None, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "customers_designer"

class DecorationCompany(models.Model):
    """
        装修公司
    """
    account = models.OneToOneField('CustomerAccount', related_name='decoration_company', default=None, null=True,
                                   blank=True, on_delete=models.SET_NULL)
    other_account = models.OneToOneField('OtherAccount', related_name='decoration_company', default=None, null=True,
                                         blank=True, on_delete=models.SET_NULL)
    # 注册号
    register_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 身份信息
    cert_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 银行帐号
    bank_no = models.CharField(max_length=50, default=None, null=True, blank=True)
    # 营业执照
    business_license = models.FileField(default=None, null=True, blank=True, upload_to=get_resources_path())
    # 省
    province = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 市
    city = models.CharField(max_length=200, default=None, null=True, blank=True)
    # 区
    area = models.CharField(max_length=200, default=None, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "customers_decorationcompany"

class DesignerDistributor(models.Model):
    """
        设计师、供应商中介表
    """
    designer = models.ForeignKey('Designer')
    distributor = models.ForeignKey('Distributor')

    class Meta:
        db_table = "customers_designerdistributor"

class FeedbackMessage(models.Model):
    """
        用户反馈信息表
    """
    # 用户编码
    account_no = models.CharField(max_length=128, default=None, null=True, blank=True)
    # 用户名
    username = models.CharField(max_length=128, default=None, null=True, blank=True)
    # 真实姓名
    name = models.CharField(max_length=64, default=None, null=True, blank=True)
    # 手机号码
    phone = models.CharField(max_length=32, default=None, null=True, blank=True)
    # 社交账号
    social_no = models.CharField(max_length=32, default=None, null=True, blank=True)
    # 邮箱
    email = models.EmailField(max_length=200, default=None, null=True, blank=True)
    # 反馈信息标题
    title = models.CharField(max_length=128, default=None, null=True, blank=True)
    # 反馈信息
    message = models.TextField()
    # 反馈时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 是否激活
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "customers_feedbackmessage"
