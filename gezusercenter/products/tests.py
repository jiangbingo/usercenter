# -*- encoding: utf-8 -*-
try:
    import simplejson as json
except:
    import json
from django.core.urlresolvers import reverse
from django.test import TestCase
from products.models import Product,ProductCategory
from accounts.models import Account, AccountAdmin, AccountAdminRole
from gezbackend.utils import get_random_code, get_password

# Create your tests here.
class ProductTest(TestCase):
    def setUp(self):
        #创建用户并登录
        security = get_random_code()
        account,flag = Account.objects.get_or_create(username='test',email='test@test.com',security=security,password=get_password('password',security))
        account_role,flag = AccountAdminRole.objects.get_or_create(name='管理员',description='管理员',permission='管理员',status=1,)
        account_admin,flag = AccountAdmin.objects.get_or_create(user=account,role=account_role,work_id='100101010',realname='测试员',department='测试员',status=1)
        first_category,flag = ProductCategory.objects.get_or_create(name='测试一级分类',step=1)
        second_category,flag = ProductCategory.objects.get_or_create(name='测试二级分类',step=2,parent_category=first_category)
        third_category,flag = ProductCategory.objects.get_or_create(name='测试三级分类',step=3,parent_category=second_category)

        Product.objects.get_or_create(name="产品1",category=third_category,type=0)
        Product.objects.get_or_create(name="产品2", category=third_category,
                                      type=1)


    def test_product_list(self):
        self.client.post('/accounts/login/',{'username':'test','password':'password'})
        response = self.client.get('/product/pdt/?type=0')

    def test_model_list(self):
        self.client.post('/accounts/login/',
                         {'username': 'test', 'password': 'password'})
        response = self.client.get('/product/pdt/?type=1')

    def test_sdk_list(self):
        self.client.post('/accounts/login/',
                         {'username': 'test', 'password': 'password'})
        response = self.client.get('/sdk/product/')

    def test_sdk_product_detail(self):
        self.client.post('/accounts/login/',
                         {'username': 'test', 'password': 'password'})
        products = json.loads(self.client.get('/sdk/product/').content)
        product_detail = self.client.get('/sdk/product/%s/' % products[0]['id'])