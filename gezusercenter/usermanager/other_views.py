# -- encoding: utf-8 --

try:
    import simplejson as json
except:
    import json
import base64

from django.core.files.base import ContentFile
from django.http import HttpResponse
from sdk.pre_check import PermissionCheck
from toolkit.mylogger import Logger

from .models import (OtherAccount, Designer, Distributor)
from .user_views import get_request_data


class SyncMessage(PermissionCheck):
    """
        第三方用户同步角色信息
    """

    @classmethod
    def run(cls, request, param):
        """
        :param request:
        :param param:
        :return:
        """
        request_data = get_request_data(request)
        username = request_data.get("username")
        app_secret = request.META.get("HTTP_SECDATA", "")
        # import ipdb;ipdb.set_trace()
        account = OtherAccount.objects.filter(username=username, app_secret=app_secret).first()
        if account is None:
            response = {"code": 1, "msg": "用户不存在.......", "content": ""}
        else:
            if param == "syncrole":
                response = cls.sync_role(request_data, account)
            elif param == "syncinfo":
                response = cls.sync_personalinfo(request_data, account)
            else:
                response = {"code": 5, "msg": "url error......", "content": ""}
        return cls._response(response)

    @classmethod
    def sync_role(cls, request_data, account):
        """
        :param request_data:
        :param account:
        :return:
        """
        # account = OtherAccount.objects.filter(id=cache_data.get("uid")).first()
        # if account is None:
        #     return {"code": 4, "msg": "can not find ther user......", "content": ""}
        # if request_data.get("username") != cache_data.get("username"):
        #     return {"code": 2, "msg": "username is invalid.......", "content": ""}
        role = int(request_data.get("role", -1))
        if role in account.get_role:
            return {"code": 4, "msg": "the user already has the role.", "content": ""}
        if role == 1:
            response = cls.sync_designer(request_data, account, role)
        elif role == 2 or role == 3:
            response = cls.sync_distributor(request_data, account, role)
        else:
            response = {"code": 3, "msg": "wrong role value.......", "content": ""}
        return response

    @classmethod
    def sync_personalinfo(cls, request_data, account):
        """
        :param request_data:
        :param account:
        :return:
        """
        return {"code": 0, "msg": "接口正在完成中......", "content": ""}

    @staticmethod
    def sync_designer(request_data, account, role):
        """
        :param request_data:
        :param account:
        :param role:
        :return:
        """
        real_name = request_data.get("real_name", "")
        cert_no = request_data.get("cert_no", "")
        design_style = request_data.get("design_style", "")
        gender = str(request_data.get("gender", ""))
        gender_map = {"0": 0, "1": 1}
        if real_name == "" or cert_no == "" or design_style == "" or gender == "":
            return {"code": 2, "msg": "parameters is not completed.", "content": ""}
        try:
            designer = Designer(other_account=account, cert_no=cert_no, real_name=request_data.get("real_name"),
                                social_account=request_data.get("social_account"), gender=gender_map.get(gender, 0),
                                phone=request_data.get("phone"), company_name=request_data.get("company"),
                                province=request_data.get("province"), city=request_data.get("city"),
                                area=request_data.get("area"), company_address=request_data.get("company_address"),
                                design_style=design_style, personal_profile=request_data.get("personal_profile"))
            cert_attachment_front = request_data.get("cert_attachment_front", "{}")
            try:
                cert_attachment_front = json.loads(cert_attachment_front)
                cert_attachment_front_name = cert_attachment_front.get("name", "")
                if cert_attachment_front_name != "" and cert_attachment_front_name is not None:
                    file_name = account.username + cert_attachment_front_name + cert_attachment_front.get("type", "")
                    designer.cert_attachment_front.save(file_name, ContentFile(base64.b64decode(
                        cert_attachment_front.get("content", ""))))
                else:
                    return {"code": 2, "msg": "parameters is not completed.", "content": ""}
            except Exception, e:
                Logger.info("synchronize designer error,save cert_attachment_front image failed: {}".format(e))
                return {"code": 2, "msg": "parameters is not completed.", "content": ""}
            cert_attachment_back = request_data.get("cert_attachment_back", "{}")
            try:
                cert_attachment_back = json.loads(cert_attachment_back)
                cert_attachment_back_name = cert_attachment_back.get("name", "")
                if cert_attachment_back_name != "" and cert_attachment_back_name is not None:
                    file_name = account.username + cert_attachment_back_name + cert_attachment_back.get("type", "")
                    designer.cert_attachment_back.save(file_name, ContentFile(base64.b64decode(
                        cert_attachment_back.get("content", ""))))
                else:
                    return {"code": 2, "msg": "parameters is not completed.", "content": ""}
            except Exception, e:
                Logger.info("synchronize designer error,save cert_attachment_back image failed: {}".format(e))
                return {"code": 2, "msg": "parameters is not completed.", "content": ""}
            designer_cert_front = request_data.get("designer_cert_front", "{}")
            try:
                designer_cert_front = json.loads(designer_cert_front)
                designer_cert_front_name = designer_cert_front.get("name", "")
                if designer_cert_front_name != "" and designer_cert_front_name is not None:
                    file_name = account.username + designer_cert_front_name + designer_cert_front.get("type", "")
                    designer.designer_cert_front.save(file_name, ContentFile(base64.b64decode(
                        designer_cert_front.get("content", ""))))
            except Exception, e:
                Logger.info("synchronize designer error,save designer_cert_front image failed: {}".format(e))
            designer_cert_back = request_data.get("designer_cert_back", "{}")
            try:
                designer_cert_back = json.loads(designer_cert_back)
                designer_cert_back_name = designer_cert_back.get("name", "")
                if designer_cert_back_name != "" and designer_cert_back_name is not None:
                    file_name = account.username + designer_cert_back_name + designer_cert_back.get("type", "")
                    designer.designer_cert_back.save(file_name, ContentFile(base64.b64decode(
                        designer_cert_back.get("content", ""))))
            except Exception, e:
                Logger.info("synchronize designer error,save designer_cert_back image failed: {}".format(e))
            designer.save()
            response_data = {"code": 0, "msg": "synchronize designer successful.", "content": ""}
        except Exception, e:
            Logger.error("apply desinger error: {}".format(e))
            response_data = {"code": 2, "msg": "param is invalid！", "content": ""}
        account.set_role(role)
        return response_data

    @staticmethod
    def sync_distributor(request_data, account, role):
        """
        :param request_data:
        :param account:
        :param role:
        :return:
        """
        real_name = request_data.get("real_name", "")
        gender = str(request_data.get("gender", ""))
        gender_map = {"0": 0, "1": 1}
        cert_no = request_data.get("cert_no", "")
        company_name = request_data.get("company_name", "")
        domain_name = request_data.get("domain_name", "")
        register_no = request_data.get("register_no", "")
        bank_no = request_data.get("bank_no", "")
        province = request_data.get("province", "")
        if (real_name == "" or gender == "" or cert_no == "" or company_name == "" or province == ""
                or domain_name == "" or register_no == "" or bank_no == ""):
            return {"code": 2, "msg": "parameters is not completed.", "content": ""}
        distributor = Distributor(other_account=account, cert_no=cert_no, name=real_name, register_no=register_no,
                                  bank_no=bank_no, company_name=company_name, gender=gender_map.get(gender, 0),
                                  location=request_data.get("location"), domain=request_data.get("domain"),
                                  domain_name=domain_name, description=request_data.get("domain_description"),
                                  province=province, city=request_data.get("city"), area=request_data.get("area"),
                                  company_address=request_data.get("company_address"))
        license_file = request_data.get("business_license", "")
        if license_file != "":
            try:
                license_file = json.loads(license_file)
                file_name = "license_{0}{1}.{2}".format(account.username, license_file.get("name", ""),
                                                        license_file.get("type", "jpg"))
                distributor.business_license.save(file_name, ContentFile(base64.b64decode(license_file.get("content",
                                                                                                           ""))))
            except Exception, e:
                Logger.error("decode avatar data error: {}".format(e))
                return {"code": 2, "msg": "parameters is not completed.", "content": ""}
        else:
            Logger.info("business_lincese file is null")
            return {"code": 2, "msg": "parameters is not completed.", "content": ""}
        image_file = request_data.get("image", "")
        if image_file != "":
            try:
                image_file = json.loads(image_file)
                file_name = "company_{0}{1}.{2}".format(account.username, image_file.get("name", ""),
                                                        image_file.get("type", "jpg"))
                distributor.image.save(file_name, ContentFile(base64.b64decode(image_file.get("content", ""))))
            except Exception, e:
                Logger.error("decode avatar data error: {}".format(e))
        else:
            Logger.info("company image file is null")
        account.set_role(role)
        distributor.save()
        return {"code": 0, "msg": "synchronize distributor successful！", "content": ""}

    @staticmethod
    def _response(response_data):
        """
        :param response_data:
        :return:
        """
        response = HttpResponse(json.dumps(json.dumps(response_data)), content_type="application/json")
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "Access-Control-Allow-Origin, x-requested-with, content-type"
        return response