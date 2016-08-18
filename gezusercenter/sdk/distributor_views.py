# -*- encoding: utf-8 -*-
__author__ = 'PD-002'

try:
    import simplejson as json
except:
    import json
import datetime
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from usermanager.models import CustomerAccount, AccountKey, PendingApprove, ApproveLog
from products.models import CustomerManufactor
from toolkit.mylogger import Logger
from .pre_check import PermissionCheck

class DistributorViewSet(PermissionCheck, viewsets.ViewSet):
    """
        获取厂商认证、供应商认证接口
    """
    def create(self, request):
        """
        :param request:
        :return:
        """
        if request.method == "GET":
            print "get", request.GET
        else:
            print "post", request.POST
        return Response(json.dumps({}), status.HTTP_200_OK)

    def list(self, request):
        """
        :param request:
        :return:
        """
        if request.method == "GET":
            print "get", request.GET
        else:
            print "post", request.POST
        return Response(json.dumps({}), status.HTTP_200_OK)

    @list_route(methods=['get', 'post'])
    def offer(self, request):
        """
        :param request:
        :return: 提供经销授权
        """
        request_data = self._get_request_data(request)
        account = None
        key = AccountKey.objects.filter(app_secret=request.META.get("HTTP_SECDATA",
                    "")).select_related("account__distributors", "account__manufactory").first()
        if key:
            account = key.account
        if account is None:
            return self._return({"code": 1, "msg": "can not find account.", "content": ""})
        if not hasattr(account, "manufactory"):
            return self._return({"code": 4, "msg": "Permission denied.", "content": ""})
        who = CustomerAccount.objects.filter(id=request_data.get("id")).first()
        if who is None:
            return self._return({"code": 2, "msg": "can not find manufactory.", "content": ""})
        product_no = request_data.get("product_no", "")
        if product_no == "" or product_no is None:
            ptype = 3
        else:
            ptype = 5
        try:
            dt = account.distributors
            manu = account.manufactory
            pending = PendingApprove(account=account, grant_to=who.distributors, contact_no=manu.contact_no, type=ptype,
                                     contact=manu.contact, register_no=dt.register_no, manufactory=dt.name,
                                     product_no=request_data.get("product_no"), business_license=dt.business_license,
                                     province=manu.province, city=manu.city, area=manu.area, image=manu.image)
            pending.save()
        except Exception, e:
            Logger.error("offer accredit error: {}".format(e))
            return self._return({"code": 3, "msg": "offer failed.:{}".format(e), "content": ""})
        return self._return({"code": 0, "msg": "offer successful.", "content": ""})

    @list_route(methods=['get', 'post'])
    def query(self, request):
        """
        :param request:
        :return: 查询经销商
        """
        request_data = self._get_request_data(request)
        name = request_data.get("name")
        if name == "" or name is None:
            accounts = CustomerAccount.objects.filter((Q(role=2) | Q(role=3) | Q(role=5)) &
                                                      Q(approved=True)).prefetch_related("manufactory")
        else:
            accounts = CustomerAccount.objects.filter((Q(role=2) | Q(role=3) | Q(role=5)) &
                                                      Q(distributors__name__contains=name)
                                                      & Q(approved=True)).prefetch_related("manufactory")
        response = []
        if accounts.exists():
            username = request_data.get("username")
            myaccount = self._get_myself(username, request.META.get("HTTP_SECDATA", ""))
            if myaccount is None:
                return self._return({"code": 2, "msg": "can not find who you are.", "content": ""})
            for account in accounts:
                if myaccount == account:
                    continue
                if hasattr(myaccount, "manufactory"):
                    if CustomerManufactor.objects.filter(manufactor=myaccount.manufactory, customer=account).first():
                        continue
                data = {
                    "id": account.id,
                    "domain_name": account.distributors.name,
                    "register_no": account.distributors.register_no,
                    "register_date": account.register_date.strftime("%Y-%M-%d: %H:%m:%S"),
                    "real_name": account.real_name,
                    "phone": account.phone,
                    "approved": 0,
                }
                if hasattr(account, "manufactory"):
                    manufacoty = account.manufactory
                    data["real_name"] = manufacoty.contact
                    data["phone"] = manufacoty.contact_no
                    data["province"] = manufacoty.province
                    data["city"] = manufacoty.city
                    data["area"] = manufacoty.area
                response.append(data)
            return self._return({"code": 0, "msg": "query data successful.", "content": response})
        else:
            return self._return({"code": 1, "msg": "can not find any distributor.", "content": ""})

    @list_route(methods=['get', 'post'])
    def queryaccredit(self, request):
        """
        :param request:
        :return: 查询合作经销商
        """
        request_data = self._get_request_data(request)
        username = request_data.get("username")
        account = self._get_myself(username, request.META.get("HTTP_SECDATA", ""))
        if account is None:
            return self._return({"code": 1, "msg": "can not find account.", "content": ""})
        pendings = PendingApprove.objects.filter(Q(type__gt=2) & (Q(account=account) |
                                        Q(grant_to=account.distributors))).select_related("account__manufactory",
                                        "grant_to__account")
        response = []
        if pendings.exists():
            for pending in pendings:
                if pending.account == account:
                    to_distributor = pending.grant_to
                    data = {
                        "register_no": to_distributor.register_no,
                        "contact": to_distributor.account.real_name,
                        "contact_no": to_distributor.account.phone,
                        "manufactory": to_distributor.name,
                        "brand": "",
                        "series": "",
                        "product_no": "",
                        "no": pending.id,
                        "from": pending.account.id,
                        "to": to_distributor.account.id,
                        "province": "",
                        "city": "",
                        "area": "",
                        "type": "out"}
                else:
                    data = {
                        "register_no": pending.register_no,
                        "contact": pending.contact,
                        "contact_no": pending.contact_no,
                        "manufactory": pending.manufactory,
                        "brand": pending.brand,
                        "series": pending.series,
                        "product_no": pending.product_no,
                        "no": pending.id,
                        "from": pending.account.id,
                        "to": pending.grant_to.account.id,
                        "province": pending.province,
                        "city": pending.city,
                        "area": pending.area,
                        "type": "in"}
                if pending.approve_log.all().exists():
                    if pending.approved:
                        data["status"] = 0
                        if pending.type == 3:
                            manu1 = -1
                            manu2 = -1
                            if hasattr(pending.account, "manufactory"):
                                manu1 = pending.account.manufactory
                            if hasattr(pending.grant_to.account, "manufactory"):
                                manu2 = pending.grant_to.account.manufactory
                            if CustomerManufactor.objects.filter((Q(manufactor=manu1) &
                                                            Q(customer=pending.grant_to.account)) |
                                                            (Q(manufactor=manu2) &
                                                            Q(customer=pending.account))).first() is None:
                                data["status"] = 2
                        elif pending.type == 4:
                            pass
                        elif pending.type == 5:
                            pass
                    else:
                        data["status"] = 1
                else:
                    data["status"] = -1
                response.append(data)
        return self._return({"code": 0, "msg": "query accredit records successful.", "content": response})

    @list_route(methods=['get', 'post'])
    def confirm(self, request):
        request_data = self._get_request_data(request)
        username = request_data.get("username")
        account = self._get_myself(username, request.META.get("HTTP_SECDATA", ""))
        if account is None:
            return self._return({"code": 1, "msg": "can not find account.", "content": ""})
        flag = request_data.get("flag", 0)
        pending = PendingApprove.objects.filter(id=int(request_data.get("no"))).select_related("grant_to__account",
                                                                            "account__manufactory").first()
        if pending and pending.grant_to.account == account:
            if int(flag) == 0:
                ApproveLog(account=account, approve_info=pending, action_date=datetime.datetime.now(),
                           message=request_data.get("message"), approved=True, action_user=account.username).save()
                pending.approved = True
                pending.save()
                try:
                    CustomerManufactor(customer=pending.grant_to.account, manufactor=pending.account.manufactory).save()
                except Exception, e:
                    Logger.error("the source user has no accredit.:{}".format(e))
                    return self._return({"code": 3, "msg": "{}".format(e), "content": ""})
            else:
                ApproveLog(account=account, approve_info=pending, action_date=datetime.datetime.now(),
                           message=request_data.get("message"), approved=False, action_user=account.username).save()
            return self._return({"code": 0, "msg": "response accredit successful.", "content": ""})
        else:
            return self._return({"code": 2, "msg": "can not find the accredit record.", "content": ""})

    @list_route(methods=['get', 'post'])
    def cancel(self, request):
        """
        :param request:
        :return:
        """
        # import ipdb;ipdb.set_trace()
        request_data = self._get_request_data(request)
        username = request_data.get("username")
        account = self._get_myself(username, request.META.get("HTTP_SECDATA", ""))
        if account is None:
            return self._return({"code": 1, "msg": "can not find account.", "content": ""})
        mtype = request_data.get("type")
        come = int(request_data.get("from"))
        to_who = int(request_data.get("to"))
        if (mtype == "out" and account.id == come) or (mtype == "in" and account.id == to_who):
            customer = CustomerManufactor.objects.filter(customer_id=to_who, manufactor__manufacturer_id=come).first()
            if customer:
                customer.delete()
            return self._return({"code": 0, "msg": "cancel accredit successful.", "content": ""})
        else:
            return self._return({"code": 2, "msg": "operation mistake.", "content": ""})

    @list_route(methods=['get', 'post'])
    def update(self, request):
        """
        :param request:
        :return:
        """
        pass

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
