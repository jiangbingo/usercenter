#!-*-encoding: utf-8 -*-
__author__ = 'PD-002'

try:
    import simplejson as json
except:
    import json
import base64
from django.core.files.base import ContentFile
from django.core.cache import cache
from .models import PendingApprove, CustomerAccount, Designer
from toolkit.mylogger import Logger
from .user_views import get_request_data, my_response

class DesignerView:
    """
        设计师认证接口
    """
    @classmethod
    def run(cls, request, param):
        """
        :param request: 请求信息
        :param param: 路径参数
        :return:
        """
        Logger.debug("get cmd designer certify, param is :{}.".format(param))
        request_data = get_request_data(request)
        callback = request_data.get("jsoncallback", "")
        account = cls._get_account(request_data)
        if account is None:
            response_data = {"code": 1, "msg": "login timeout or username is invalid！", "content": ""}
        else:
            if param == "apply":
                response_data = cls.apply(account, request_data)
            elif param == "query":
                response_data = cls.query(account)
            elif param == "update":
                response_data = cls.update(account, request_data)
            elif param == "check":
                response_data = cls.check(request_data.get("cert_no"))
            else:
                response_data = {"code": 2, "msg": "url wrong！", "content": ""}
        return my_response(response_data, callback)

    @classmethod
    def apply(cls, account, request_data):
        """
        上传授权信息
        :param account:
        :param request_data:
        :param files:
        :return:
        """
        real_name = request_data.get("real_name", "")
        cert_no = request_data.get("cert_no", "")
        design_style = request_data.get("design_style", "")
        # if account.role != 0:
        #     return {"code": 3, "msg": "only normal account can apply designer certify.", "content": ""}
        if real_name == "" or cert_no == "" or design_style == "":
            return {"code": 4, "msg": "parameters is not completed.", "content": ""}
        try:
            pending = PendingApprove(account=account, role=PendingApprove.ROLE_DESIGNER, cert_no=cert_no,
                                     type=PendingApprove.TYPE_CERTIFY, real_name=request_data.get("real_name"),
                                     social_account=request_data.get("social_account"),
                                     gender=request_data.get("gender", 0),
                                     contact_no=request_data.get("phone"), company_name=request_data.get("company"),
                                     province=request_data.get("province"), city=request_data.get("city"),
                                     area=request_data.get("area"), company_address=request_data.get("company_address"),
                                     design_style=design_style, personal_profile=request_data.get("personal_profile"))
            cert_attachment_front = request_data.get("cert_attachment_front", "{}")
            try:
                cert_attachment_front = json.loads(cert_attachment_front)
                cert_attachment_front_name = cert_attachment_front.get("name", "")
                if cert_attachment_front_name != "" and cert_attachment_front_name is not None:
                    file_name = account.username + cert_attachment_front_name + cert_attachment_front.get("type", "")
                    pending.cert_attachment_front.save(file_name, ContentFile(base64.b64decode(
                        cert_attachment_front.get("content", ""))))
            except Exception, e:
                Logger.info("apply designer upload message error,save cert_attachment_front image failed: {}".format(e))
            cert_attachment_back = request_data.get("cert_attachment_back", "{}")
            try:
                cert_attachment_back = json.loads(cert_attachment_back)
                cert_attachment_back_name = cert_attachment_back.get("name", "")
                if cert_attachment_back_name != "" and cert_attachment_back_name is not None:
                    file_name = account.username + cert_attachment_back_name + cert_attachment_back.get("type", "")
                    pending.cert_attachment_back.save(file_name, ContentFile(base64.b64decode(
                        cert_attachment_back.get("content", ""))))
            except Exception, e:
                Logger.info("apply designer upload message error,save cert_attachment_back image failed: {}".format(e))
            designer_cert_front = request_data.get("designer_cert_front", "{}")
            try:
                designer_cert_front = json.loads(designer_cert_front)
                designer_cert_front_name = designer_cert_front.get("name", "")
                if designer_cert_front_name != "" and designer_cert_front_name is not None:
                    file_name = account.username + designer_cert_front_name + designer_cert_front.get("type", "")
                    pending.designer_cert_front.save(file_name, ContentFile(base64.b64decode(
                        designer_cert_front.get("content", ""))))
            except Exception, e:
                Logger.info("apply designer upload message error,save designer_cert_front image failed: {}".format(e))
            designer_cert_back = request_data.get("designer_cert_back", "{}")
            try:
                designer_cert_back = json.loads(designer_cert_back)
                designer_cert_back_name = designer_cert_back.get("name", "")
                if designer_cert_back_name != "" and designer_cert_back_name is not None:
                    file_name = account.username + designer_cert_back_name + designer_cert_back.get("type", "")
                    pending.designer_cert_back.save(file_name, ContentFile(base64.b64decode(
                        designer_cert_back.get("content", ""))))
            except Exception, e:
                Logger.info("apply designer upload message error,save designer_cert_back image failed: {}".format(e))
            pending.save()
            response_data = {"code": 0, "msg": "apply designer certify successful.", "content": ""}
        except Exception, e:
            Logger.error("apply desinger error: {}".format(e))
            response_data = {"code": 5, "msg": "param is invalid！", "content": ""}
        return response_data

    @classmethod
    def query(cls, account):
        """
        上传认证信息
        :param account:
        :return:
        """
        data = {"username": account.username}
        pending = PendingApprove.objects.filter(account=account, role=1).prefetch_related("approve_log").last()
        data["message"] = None
        if pending is None:
            data["status"] = -1
        else:
            data["real_name"] = pending.real_name
            if hasattr(pending, "approve_log"):
                data["message"] = pending.approve_log.last().message
                if pending.approved:
                    data["status"] = 0
                else:
                    data["status"] = 2
            else:
                data["status"] = 1
        return {"code": 0, "msg": "query data successful.", "content": data}

    @staticmethod
    def check(cert_no):
        """
        :param cert_no:
        :return:
        """
        if Designer.objects.filter(cert_no=cert_no).first():
            return {"code": 0, "msg": "this cert_no is already existed.", "content": ""}
        else:
            return {"code": -1, "msg": "can't find this cert_no.", "content": ""}

    @classmethod
    def update(cls, account, request_data):
        """
        :param account:
        :param request_data:
        :param files:
        :return:
        """
        if not hasattr(account, "designer"):
            return {"code": 4, "msg": "designer is not certified.", "content": ""}
        designer = account.designer
        try:
            social_account = request_data.get("social_account", "")
            if social_account != "":
                designer.social_account = social_account
            company = request_data.get("company", "")
            if company != "":
                designer.company_name = company
            province = request_data.get("province", "")
            if province != "":
                designer.province = province
            city = request_data.get("city", "")
            if city != "":
                designer.city = city
            area = request_data.get("area", "")
            if area != "":
                designer.area = area
            company_address = request_data.get("company_address", "")
            if company_address != "":
                designer.company_address = company_address
            design_style = request_data.get("design_style", "")
            if design_style != "":
                designer.design_style = design_style
            personal_profile = request_data.get("personal_profile", "")
            if personal_profile != "":
                designer.persional_profile = personal_profile
            designer_cert_front = request_data.get("designer_cert_front", "{}")
            try:
                designer_cert_front = json.loads(designer_cert_front)
                designer_cert_front_name = designer_cert_front.get("name", "")
                if designer_cert_front_name != "" and designer_cert_front_name is not None:
                    file_name = account.username + designer_cert_front_name + designer_cert_front.get("type", "")
                    designer.designer_cert_front.delete(save=False)
                    designer.designer_cert_front.save(file_name, ContentFile(base64.b64decode(
                        designer_cert_front.get("content", ""))))
            except Exception, e:
                Logger.info("update designer message error,save designer_cert_front image failed: {}".format(e))
            designer_cert_back = request_data.get("designer_cert_front", "{}")
            try:
                designer_cert_back = json.loads(designer_cert_back)
                designer_cert_back_name = designer_cert_back.get("name", "")
                if designer_cert_back_name != "" and designer_cert_back_name is not None:
                    file_name = account.username + designer_cert_back_name + designer_cert_back.get("type", "")
                    designer.designer_cert_front.delete(save=False)
                    designer.designer_cert_back.save(file_name, ContentFile(base64.b64decode(
                        designer_cert_back.get("content", ""))))
            except Exception, e:
                Logger.info("update designer message error,save designer_cert_back image failed: {}".format(e))
            designer.save()
            response_data = {"code": 0, "msg": "update designer message successful.", "content": ""}
        except Exception, e:
            Logger.error("apply desinger error: {}".format(e))
            response_data = {"code": 3, "msg": "param is invalid : {}.".format(e), "content": ""}
        return response_data

    @staticmethod
    def _get_account(request_data):
        session_id = request_data.get("sid")
        name = request_data.get("username")
        cache_data = cache.get(session_id)
        if cache_data is None:
            username = ""
        else:
            username = cache_data.get("username")
        if name is None or username != name:
            Logger.info("get username is invalid.")
            return None
        return CustomerAccount.objects.filter(username=username).first()
