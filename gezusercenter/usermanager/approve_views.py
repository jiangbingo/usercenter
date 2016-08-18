#!-*-encoding: utf-8 -*-
__author__ = 'PD-002'

try:
    import simplejson as json
except:
    import json
import base64
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from toolkit.mylogger import Logger
from .user_views import get_request_data, my_response
from .models import CustomerAccount, PendingApprove, Distributor

class MessageView:
    """
        编辑用户认证授权信息
    """
    @classmethod
    def run(cls, request, param):
        """
        :param request: 请求信息
        :param param: 路径参数
        :return:
        """
        Logger.debug("get cmd edit message!")
        request_data = get_request_data(request)
        callback = request_data.get("jsoncallback", "")
        if param == "uploadcertify":
            Logger.debug("edit authentication message cmd is uploadcertify!")
            response = cls.uploadcertify(request_data)
        elif param == "get":
            Logger.debug("edit authentication message cmd is get!")
            response = cls.query(request_data)
        elif param == "uploadapprove":
            Logger.debug("edit authentication message cmd is uploadapprove!")
            response = cls.uploadapprove(request_data)
        elif param == "update":
            Logger.debug("edit authentication message cmd is update")
            response = cls.update(request_data)
        else:
            Logger.info("edit authentication message cmd is wrong: {}!".format(param))
            response = {"code": 4, "msg": "url error.", "content": ""}
        return my_response(response, callback)

    @classmethod
    def uploadapprove(cls, requst_data):
        """
            上传授权信息
            :param requst_data:
            :return:
        """
        account = cls._get_account(requst_data)
        if account is None:
            return {"code": 1, "msg": "login timeout！", "content": ""}
        role = requst_data.get("role", "")
        if int(role) != 2 and int(role) != 3:
            return {"code": 2, "msg": "user's role is invalid！", "content": ""}
        domain = requst_data.get("domain", "")
        domain_name = requst_data.get("domain_name", "")
        domain_description = requst_data.get("domain_description", "")
        if role == "" or domain == "" or domain_name == "" or domain_description == "":
            return {"code": 3, "msg": "parameters error", "content": ""}
        if account.certified:
            last_approve = account.pending_approves.all().last()
            approve = PendingApprove(role=role, domain=domain, domain_name=domain_name, cert_no=last_approve.cert_no,
                                     domain_description=domain_description, type=1, account=account,
                                     register_no=last_approve.register_no, bank_no=last_approve.bank_no,
                                     gender=last_approve.gender, real_name=last_approve.real_name,
                                     province=last_approve.province, city=last_approve.city, area=last_approve.area,
                                     company_name=last_approve.company_name, image=last_approve.image,
                                     business_license=last_approve.business_license,
                                     company_address=last_approve.company_address)
            try:
                approve.save()
            except Exception, e:
                return {"code": 6, "msg": e, "content": ""}
            return {"code": 0, "msg": "upload approved successful！", "content": ""}
        else:
            return {"code": 5, "msg": "user is not certified！", "content": ""}

    @classmethod
    def uploadcertify(cls, request_data):
        """
        上传认证信息
        :param files:
        :param request_data:
        :return:
        """
        account = cls._get_account(request_data)
        if account is None:
            return {"code": 1, "msg": "login timeout！", "content": ""}
        role = int(request_data.get("role", 2))
        if role == 2 or role == 3:
            pendding = PendingApprove(role=role, account=account, cert_no=request_data.get("cert_no"),
                                      register_no=request_data.get("register_no"), bank_no=request_data.get("bank_no"),
                                      company_name=request_data.get("company_name"), gender=request_data.get("gender"),
                                      real_name=request_data.get("real_name"), province=request_data.get("province"),
                                      city=request_data.get("city"), area=request_data.get("area"),
                                      company_address=request_data.get("company_address"))
            license_file = request_data.get("business_license", "")
            if license_file != "":
                try:
                    license_file = json.loads(license_file)
                    file_name = "license_{0}{1}.{2}".format(account.username, license_file.get("name", ""),
                                                            license_file.get("type", "jpg"))
                    pendding.business_license.save(file_name, ContentFile(base64.b64decode(license_file.get("content",
                                                                                                            ""))))
                except Exception, e:
                    Logger.error("decode avatar data error: {}".format(e))
            else:
                Logger.info("business_lincese file is null")
            image_file = request_data.get("image", "")
            if image_file != "":
                try:
                    image_file = json.loads(image_file)
                    file_name = "company_{0}{1}.{2}".format(account.username, image_file.get("name", ""),
                                                            image_file.get("type", "jpg"))
                    pendding.image.save(file_name, ContentFile(base64.b64decode(image_file.get("content", ""))))
                except Exception, e:
                    Logger.error("decode avatar data error: {}".format(e))
            else:
                Logger.info("company image file is null")
            try:
                pendding.save()
            except Exception, e:
                return{"code": 3, "msg": "uploadcertify save pendding error: {}!".format(e), "content": ""}
        return {"code": 0, "msg": "upload certified successful！", "content": ""}

    @classmethod
    def query(cls, request_data):
        """
        :param request_data:
        :return:
        """
        account = cls._get_account(request_data)
        if account is None:
            return {"code": 1, "msg": "login timeout！", "content": ""}
        user_message = {}
        approves = account.pending_approves.filter(Q(Q(type=0) | Q(type=1)) & Q(Q(role=2) | Q(role=3)))
        if approves.exists():
            approve = approves.last()
            user_message["role"] = [approve.role]
            user_message["register_no"] = approve.register_no
            user_message["cert_no"] = approve.cert_no
            user_message["bank_no"] = approve.bank_no
            user_message["domain"] = approve.domain
            user_message["domain_name"] = approve.domain_name
            user_message["company_name"] = approve.company_name
            user_message["domain_description"] = approve.domain_description
            user_message["gender"] = approve.gender
            user_message["company_address"] = approve.company_address
            user_message["real_name"] = approve.real_name
            user_message["province"] = approve.province
            user_message["city"] = approve.city
            user_message["area"] = approve.area
            if approve.business_license.name != "":
                business_url = settings.SERVER_WEBSITE + settings.MEDIA_URL[1:] + approve.business_license.name
                user_message["business_license_url"] = business_url
                user_message["business_license"] = base64.b64encode(approve.business_license.read())
                approve.business_license.close()
            else:
                user_message["business_license"] = None
                user_message["business_license_url"] = None
            if approve.image.name != "":
                image_url = settings.SERVER_WEBSITE + settings.MEDIA_URL[1:] + approve.image.name
                user_message["image_url"] = image_url
                user_message["image"] = base64.b64encode(approve.image.read())
                approve.image.close()
            else:
                user_message["image"] = None
                user_message["image_url"] = None
            user_message["certified"] = 2
            if approve.type == 1:
                user_message["certified"] = 0
                if approve.approve_log.exists():
                    if approve.approved:
                        user_message["approved"] = 0
                    else:
                        user_message["approved"] = 1
                else:
                    user_message["approved"] = 2
            else:
                user_message["approved"] = -1
                if approve.approve_log.exists():
                    if account.certified:
                        user_message["certified"] = 0
                    else:
                        user_message["certified"] = 1
        else:
            user_message["role"] = account.get_role
            user_message["certified"] = -1
            user_message["approved"] = -1
        if hasattr(account, "distributors"):
            keys = account.distributors.key
            if keys is not None:
                user_message["token"] = keys.token
                user_message["app_secret"] = keys.app_secret
                user_message["license"] = keys.license
        return {"code": 0, "msg": "query data successful!", "content": user_message}

    @classmethod
    def update(cls, request_data):
        """
        :param request_data:
        :return:
        """
        account = cls._get_account(request_data)
        if account is None:
            return {"code": 1, "msg": "login timeout！", "content": ""}
        pending = account.pending_approves.filter(Q(Q(type=0) | Q(type=1)) & Q(Q(role=2) | Q(role=3))).last()
        if pending is None:
            return {"code": 2, "msg": "the user has not apply certified.", "content": ""}
        try:
            image_file = json.loads(request_data.get("image"))
            pending.image.delete()
            file_name = "company_{0}{1}.{2}".format(account.username, image_file.get("name", ""),
                                                    image_file.get("type", "jpg"))
            pending.image.save(file_name, ContentFile(base64.b64decode(image_file.get("content", ""))))
            pending.save()
        except Exception, e:
            Logger.error("update authentication error: {}".format(e))
            return {"code": 3, "msg": "{}".format(e), "content": ""}
        if pending.approved and pending.type == 1 and hasattr(account, "distributors"):
            account.distributors.image = pending.image
        return {"code": 0, "msg": "update successful！", "content": ""}

    @staticmethod
    def _get_account(request_data):
        session_id = request_data.get("sid")
        cache_data = cache.get(session_id)
        if cache_data is None:
            return None
        username = cache_data.get("username")
        account = CustomerAccount.objects.filter(username=username).first()
        if account is None or account.username != request_data.get("username"):
            return None
        return account
