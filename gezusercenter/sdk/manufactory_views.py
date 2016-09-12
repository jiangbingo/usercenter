# -*- encoding: utf-8 -*-
__author__ = 'PD-002'

try:
    import simplejson as json
except:
    import json
import base64

from django.core.files.base import ContentFile
from products.models import Manufactor, ProductBrand, ProductBrandSeries, CustomerManufactor
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from toolkit.mylogger import Logger
from usermanager.models import PendingApprove, CustomerAccount, AccountKey

from .pre_check import PermissionCheck


class ManufactoryViewSet(PermissionCheck, viewsets.ViewSet):
    """
        获取厂商认证、供应商认证接口
    """
    def create(self, request):
        """
        :param request:
        :return:
        """
        return Response(json.dumps({"code": -1, "msg": "error request.", "content": ""}), status.HTTP_200_OK)

    def list(self, request):
        """
        :param request:
        :return:
        """
        return Response(json.dumps({{"code": -1, "msg": "error request.", "content": ""}}), status.HTTP_200_OK)

    @list_route(methods=['get', 'post'])
    def upload(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd upload manufactory accredit.")
        request_data = self._get_request_data(request)
        username = request_data.get("username")
        account = self._get_myself(username, request.META.get("HTTP_SECDATA", ""))
        if account is None:
            return self._return({"code": 1, "msg": "can not find account.", "content": ""})
        try:
            pending = PendingApprove(account=account, register_no=request_data.get("register_no"),
                                     province=request_data.get("province"), city=request_data.get("city"),
                                     area=request_data.get("area"), contact=request_data.get("contact"),
                                     contact_no=request_data.get("contact_no"), manufactory=request_data.get("name"),
                                     type=2, role=5)
            business_license = request_data.get("business_license")
            try:
                business_license = json.loads(business_license)
                business_license_name = business_license.get("name", "")
                if business_license_name != "" and business_license_name is not None:
                    file_name = account.username + business_license_name + business_license.get("type")
                    pending.business_license.save(file_name, ContentFile(base64.b64decode(
                        business_license.get("content", ""))))
            except Exception, e:
                Logger.info("upload manufactory accredit, save business_license image failed: {}".format(e))
            avatar = request_data.get("avatar")
            try:
                avatar = json.loads(avatar)
                avatar_name = avatar.get("name", "")
                if avatar_name != "" and avatar_name is not None:
                    file_name = account.username + avatar_name + avatar.get("type")
                    pending.image.save(file_name, ContentFile(base64.b64decode(avatar.get("content", ""))))
            except Exception, e:
                Logger.info("upload manufactory accredit, save avatar image failed: {}".format(e))
            pending.save()
        except Exception, e:
            Logger.error("upload manufactory error: {}".format(e))
            return self._return({"code": 2, "msg": "{}".format(e), "content": ""})
        iself = False
        if account.distributors.register_no == request_data.get("register_no"):
            iself = True
        return self._return({"code": 0, "msg": "upload accreditmanufactory successful！",
                             "content": {"id": pending.id, "iself": iself}})

    @list_route(methods=['get', 'post'])
    def query(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd query manufactory accredit.")
        request_data = self._get_request_data(request)
        account = None
        app_secret = request.META.get("HTTP_SECDATA", "")
        keys = AccountKey.objects.filter(app_secret=app_secret).prefetch_related(
            "account__pending_approves__approve_log", "account__manufactors", "distributors")
        if keys:
            account = keys.first().account
        if account is None:
            return self._return({"code": 1, "msg": "can not find account.", "content": ""})
        response = []
        register_no = request_data.get("register_no")
        for prove in account.pending_approves.filter(type=2):
            if register_no == "" or register_no is None or prove.register_no == register_no:
                data = {"name": prove.manufactory,
                        "province": prove.province,
                        "city": prove.city,
                        "area": prove.area,
                        "contact": prove.contact,
                        "contact_no": prove.contact_no,
                        "register_no": prove.register_no,
                        "register_date": prove.create_date.strftime("%Y-%M-%d: %H:%m:%S"),
                        "iself": False,
                        "business_license": "",
                        "avatar": ""}
                if account.distributors.register_no == prove.register_no:
                    data["iself"] = True
                if prove.approve_log.all().exists():
                    if prove.approved:
                        data["status"] = 0
                        if CustomerManufactor.objects.filter(manufactor__register_no=prove.register_no,
                                                             customer_id=account.id).first() is None:
                            data["status"] = 2
                        else:
                            manu = account.manufactors.filter(register_no=prove.register_no).first()
                            if manu:
                                data["mid"] = manu.id
                    else:
                        data["status"] = 1
                else:
                    data["status"] = -1
                response.append(data)
        return self._return({"code": 0, "msg": "query data successful.", "content": response})

    @list_route(methods=['get', 'post'])
    def activate(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd activate manufactory.")
        app_secret = request.META.get("HTTP_SECDATA", "")
        key = AccountKey.objects.filter(app_secret=app_secret).select_related("account__distributors").first()
        if key is None:
            return self._return({"code": 1, "msg": "can not find the account.", "content": ""})
        account = key.account
        distributors = account.distributors
        pending = PendingApprove(account=account, register_no=distributors.register_no, manufactory=distributors.name,
                                 type=2, role=5, business_license=distributors.business_license,
                                 contact=account.real_name, contact_no=account.phone)
        pending.save()
        return self._return({"code": 0, "msg": "manufactory activate successful.", "content": ""})

    @list_route(methods=['get', 'post'])
    def cancel(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd cancel manufactory accredit.")
        request_data = self._get_request_data(request)
        username = request_data.get("username")
        account = self._get_myself(username, request.META.get("HTTP_SECDATA", ""))
        if not account:
            return self._return({"code": 1, "msg": "can not find the account.", "content": ""})
        manu = CustomerManufactor.objects.filter(manufactor__register_no=request_data.get("register_no"),
                                                 customer=account).first()
        if manu:
            manu.delete()
            return self._return({"code": 0, "msg": "delete data successful.", "content": ""})
        else:
            return self._return({"code": 2, "msg": "can not find the manufactory.", "content": ""})

    @list_route(methods=['get', 'post'])
    def addbrand(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd addbrand.")
        request_data = self._get_request_data(request)
        manu = Manufactor.objects.filter(id=int(request_data.get("mid"))).prefetch_related("brands").first()
        if manu is None:
            return self._return({"code": 2, "msg": "can not find the manufactory.", "content": ""})
        try:
            brands = json.loads(request_data.get("brands"))
            for key, values in brands.items():
                pd = manu.brands.filter(name=key).first()
                if pd is None:
                    pd = ProductBrand(name=key, no=ProductBrand.objects.all().count() + 1, manufactory=manu)
                    pd.save()
                for value in values:
                    ProductBrandSeries(brand=pd, name=value, no=ProductBrandSeries.objects.all().count() + 1).save()
        except Exception, e:
            Logger.error("add brand_series, json decode error: {}".format(e))
            return self._return({"code": 2, "msg": "{}".format(e), "content": ""})
        return self._return({"code": 0, "msg": "add brands series successful.", "content": ""})

    @list_route(methods=['get', 'post'])
    def reconnect(self, request):
        """
        :param request:
        :return: 重新获取厂家授权
        """
        Logger.debug("get cmd reget manufactory accredit.")
        request_data = self._get_request_data(request)
        account = self._get_myself(request_data.get("username"), request.META.get("HTTP_SECDATA", ""))
        if account is None:
            return self._return({"code": 1, "msg": "can not find the account.", "content": ""})
        manu = Manufactor.objects.filter(register_no=request_data.get("register_no")).first()
        if manu is None:
            return self._return({"code": 2, "msg": "can not find the manufactory.", "content": ""})
        try:
            CustomerManufactor(customer=account, manufactor=manu).save()
            return self._return({"code": 0, "msg": "reconnect manu to account successful.", "content": ""})
        except Exception, e:
            Logger.error("reconnect manu to account error: {}".format(e))
            return self._return({"code": 3, "msg": "reconnect manu to account error.", "content": ""})

    @list_route(methods=['get', 'post'])
    def query_passed(self, request):
        """
        :param request:
        :return: 获取验证通过的厂家
        """
        request_data = self._get_request_data(request)
        username = request_data.get("username")
        account = None
        if username:
            account = CustomerAccount.objects.filter(username=username).first()
        else:
            app_secret = request.META.get("HTTP_SECDATA", "")
            keys = AccountKey.objects.filter(app_secret=app_secret).select_related("account").first()
            if keys:
                account = keys.account
        if not account:
            return self._return({"code": 1, "msg": "can not find the account.", "content": ""})
        manufactories = account.manufactors.filter(active=True)
        response_data = []
        for manu in manufactories:
            data = {}
            data["id"] = manu.id
            data["rgister_no"] = manu.register_no
            data["name"] = manu.name
            data["business_license"] = ""
            # data["business_license"] = base64.b64encode(manu.business_license.read())
            response_data.append(data)
        return self._return({"code": 0, "msg": "query manufactory successful.", "content": response_data})

    @staticmethod
    def _get_myself(username, app_secret):
        account = None
        keys = AccountKey.objects.filter(app_secret=app_secret).select_related("account").first()
        if keys:
            account = keys.account
            # if account.username != username:
            #     return None
        return account

    @staticmethod
    def _get_request_data(request):
        if request.method == "GET":
            return request.GET
        else:
            return request.POST

    @staticmethod
    def _return(response):
        if response["code"] != 0:
            Logger.info("return data is: {}".format(response))
        return Response(json.dumps(response), status.HTTP_200_OK)
