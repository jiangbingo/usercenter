#!-*-encoding: utf-8 -*-
try:
    import simplejson as json
except:
    import json
import uuid
import base64
import re
from urllib import unquote, urlencode
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import SimpleTemplateResponse
from django.core.cache import cache
from django.conf import settings
from usermanager.models import *
from toolkit.utils import encrypt_passwd
from authentication.views import CheckUser
from toolkit.mylogger import Logger

class RegisterView:
    """
        注册新用户
    """
    @staticmethod
    def register(request):
        Logger.debug("get cmd register!")
        request_data = get_request_data(request)
        username = request_data.get("username", "")
        password = encrypt_passwd(request_data.get("password", ""))
        email = request_data.get("email", "")
        phone = request_data.get("phone", "")
        callback = request_data.get("jsoncallback", "")
        if "" == username or (email == "" and phone == ""):
            Logger.info("register error!")
            return my_response(json.dumps({"code": 2, "msg": "parameters is not complete.", "content": ""}), callback)
        response = {}
        try:
            users = QueryView.query_by_username(request_data)
            if users is not None:
                response = {"code": 2, "msg": "the user has registed.", "content": ""}
                return my_response(response, callback)
            if email != "":
                emails = QueryView.query_by_email(request_data)
                if emails is not None:
                    response = {"code": 2, "msg": "the email account has used.", "content": ""}
                    return my_response(response, callback)
            if phone != "":
                phones = QueryView.query_by_phone(request_data)
                if phones is not None:
                    response = {"code": 2, "msg": "the phone number has used.", "content": ""}
                    return my_response(response, callback)
            account = CustomerAccount(username=username, password=password, source=int(request_data.get("source", 0)),
                                      phone=phone, email=email, role=1)
            account.today_max_count
            account.save()
            account.generate_account_no()
            response = {"code": 0, "msg": "register account successfl.", "content": ""}
        except Exception, e:
            Logger.error("register user error: {}".format(e))
            response = {"code": 1, "msg": "server error!", "content": ""}
        return my_response(response, callback)

class RecodView:
    """
        设置获取登录记录
    """
    timeout = 3600 * 2

    @classmethod
    def set_record(cls, request):
        """
        :param request:
        :return:
        """
        request_dict = get_request_data(request).dict()
        http_referer = request_dict.get("referer")
        if cls.permission_check(request_dict):
            del request_dict["sign"]
            del request_dict["sign_type"]
            request_dict["app_secret"] = request_dict.get("sec_data")
            del request_dict["sec_data"]
            if request.META.get("HTTP_USER_AGENT", "") != "":
                request_dict["agent"] = request.META.get("HTTP_USER_AGENT")
            if request.META.get("REMOTE_ADDR", "") != "":
                request_dict["ip_address"] = request.META.get("REMOTE_ADDR")
            is_system = int(request_dict.get("is_system", 0))
            account_key = AccountKey.objects.filter(app_secret=request_dict.get("app_secret")).prefetch_related(
                "license_groups").first()
            if account_key and hasattr(account_key, "license_groups"):
                lincense_group = account_key.license_groups.first()
                if lincense_group and lincense_group.group:
                    request_dict["gid"] = account_key.license_groups.first().group.id
            if is_system == 0:
                code, session_id = cls.set_self_reord(request_dict)
            else:
                code, session_id = cls.set_other_record(request_dict)
            msg = "authentication check successful."
        else:
            code = -1
            session_id = None
            msg = "authentication check failed."
        if http_referer is None or http_referer == "":
            return HttpResponse(json.dumps({"code": code, "msg": msg, "content": {"sid": session_id}}),
                                content_type="application/json")
        else:
            url = "{0}?cd={1}&sid={2}".format(http_referer, code, session_id)
            response = HttpResponse('<html><script language="javascript">window.location = "{}";\
                        </script></html>'.format(unquote(url)))
            if session_id is not None:
                response.set_cookie(LoginView.cookie_name, session_id, cls.timeout - 2)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Headers"] = "Access-Control-Allow-Origin, x-requested-with, content-type"
            return response

    @classmethod
    def set_self_reord(cls, request_dict):
        """
        :param request_dict:
        :return:
        """
        account = CustomerAccount.objects.filter(username=request_dict.get("username")).first()
        if account is None:
            return 1, 0
        request_dict["uid"] = account.id
        request_dict["phone"] = account.phone
        request_dict["email"] = account.email
        if account.personal_info:
            url_head = settings.SERVER_WEBSITE + settings.MEDIA_URL[1:]
            if account.personal_info.avatar:
                request_dict["avatar"] = url_head + account.personal_info.avatar.name
            else:
                request_dict["avatar"] = None
        session_id = uuid.uuid4().get_hex()
        # print "self, session_id", session_id
        cache.set(session_id, request_dict, timeout=cls.timeout)
        return 0, session_id

    @classmethod
    def set_other_record(cls, request_dict):
        """
        :param request_dict:
        :return:
        """
        code = 0
        username = request_dict.get("username")
        account = OtherAccount.objects.filter(username=username, app_secret=request_dict.get("app_secret")).first()
        if account is None:
            key = AccountKey.objects.filter(app_secret=request_dict.get("app_secret")).prefetch_related(
                "distributors__account").first()
            if hasattr(key, "distributors"):
                customer = key.distributors.account
                personal_info = PersonalInfo(gold=10000)
                personal_info.save()
                account = OtherAccount(platform=customer, username=username, role=1, phone=request_dict.get("phone"),
                                       email=request_dict.get("email"), app_secret=request_dict.get("app_secret"),
                                       personal_info=personal_info)
                account.save()
                Logger.debug("create other user.")
                request_dict["uid"] = account.id
            else:
                code = -1
                Logger.error("other user has no platfrom!")
        else:
            request_dict["email"] = account.email
            request_dict["phone"] = account.phone
            request_dict["uid"] = account.id
            Logger.debug("other user is existed.")
        if code == 0:
            session_id = uuid.uuid4().get_hex()
            cache.set(session_id, request_dict, timeout=cls.timeout)
        else:
            session_id = None
        return code, session_id

    @classmethod
    def get_record(cls, request):
        """
        :param request:
        :return:
        """
        request_data = get_request_data(request)
        session_id = request.COOKIES.get(LoginView.cookie_name, "")
        http_server = request_data.get("server", "")
        if http_server == "":
            url_referer = request.META.get("HTTP_REFERER", "") + "?result=error"
            return HttpResponseRedirect(url_referer)
        param_str = "?"
        if cls.permission_check(request_data) and session_id != "" and http_server != "":
            session_data = cache.get(session_id)
            if session_data is not None:
                session_data["sid"] = session_id
                param_dict = session_data.items()
                param_str += urlencode(param_dict)
                login = True
            else:
                login = False
        else:
            login = False
        if login:
            param_str += "&login=0"
            page = "首页"
        else:
            param_str += "login=1"
            page = "登录界面"
        cache.expire(session_id, cls.timeout)
        url = unquote(http_server) + param_str
        content = {"url": url, "seconds": 3, "result": login, "page": page}
        return SimpleTemplateResponse("transfer.html", content)
        # response = HttpResponseRedirect(url)
        # response["Access-Control-Allow-Origin"] = "*"
        # response["Access-Control-Allow-Headers"] = "Access-Control-Allow-Origin, x-requested-with, content-type"
        # return response

    @classmethod
    def set_cookie(cls, request):
        """
        :param request:
        :return:
        """
        request_data = get_request_data(request)
        sid = request_data.get("sid")
        response = HttpResponse()
        response.set_cookie(LoginView.cookie_name, sid, max_age=cls.timeout - 2)
        return response

    @staticmethod
    def permission_check(meta):
        """
        :param meta:
        :return:
        """
        sign = meta.get("sign", "")
        sec_data = meta.get("sec_data", "")
        sign_type = meta.get("sign_type", "")
        if CheckUser.ck({"sec_data": unquote(sec_data), "sign": unquote(sign), "sign_type": unquote(sign_type)}):
            return True
        else:
            return False

class LoginView:
    """
        登录验证
        return code: 0 1 2 3
    """
    # 登录超时时间
    timeout = 3600 * 2
    cookie_name = "xxxsid"

    @classmethod
    def login(cls, request):
        request_data = get_request_data(request)
        callback = request_data.get("jsoncallback", "")
        user = QueryView.query_by_username(request_data)
        password = encrypt_passwd(request_data.get("password"))
        if user is None or user == -1:
            response_data = {"code": 1, "msg": "username is error.", "content": ""}
            return my_response(response_data, callback)
        if user.password != password:
            response_data = {"code": 2, "msg": "username, password error.", "content": ""}
            return my_response(response_data, callback)
        data = {"username": user.username, "phone": user.phone, "email": user.email, "role": user.get_role,
                "source": request_data.get("source"), "uid": user.id}
        if user.email_certified or user.phone_certified:
            session_id = uuid.uuid4().get_hex()
            cache.set(session_id, {"username": user.username}, cls.timeout)
            print "lid", session_id
            data["lid"] = session_id
            response_data = {"code": 0, "msg": "login successful.", "content": data}
            return my_response(response_data, callback)
        else:
            response_data = {"code": 3, "msg": "phone number and email number are not certified.", "content": data}
            return my_response(response_data, callback)

    @classmethod
    def email_code_check(cls, request):
        request_data = get_request_data(request)
        callback = request_data.get("jsoncallback", "")
        user = QueryView.query_by_username(request_data)
        if user is None or user == -1:
            response_data = {"code": 1, "msg": "user is not existed.", "content": ""}
            return my_response(response_data, callback)
        cache_code = cache.get("ecode" + user.username)
        if cache_code is None:
            return my_response({"code": 3, "msg": "checkcode expiration.", "content": {"email": user.email}}, callback)
        code = request_data.get("code")
        if code is not None and code == cache_code:
            user.email_certified = True
            user.save()
            cache.delete(user.username)
            return my_response({"code": 0, "msg": "checkcode check successful.", "content": ""}, callback)
        else:
            return my_response({"code": 2, "msg": "checkcode check failed.", "content": ""}, callback)

    @classmethod
    def get_status(cls, request):
        request_data = get_request_data(request)
        callback = request_data.get("jsoncallback", "")
        user = QueryView.query_by_username(request_data)
        if user is None or user == -1:
            response_data = {"code": 1, "msg": "user is not existed.", "content": ""}
            return my_response(response_data, callback)
        else:
            status = 1
            if user.email_certified or user.phone_certified:
                status = 0
            return my_response({"code": 0, "msg": "get user status successful.", "content": {"status": status}},
                               callback)

class LogoutView:
    """
        用户登出
    """
    @classmethod
    def logout(cls, request):
        request_data = get_request_data(request)
        session_id = request_data.get("sid")
        callback = request_data.get("jsoncallback", "")
        try:
            if session_id:
                cache_data = cache.get(session_id)
                if cache_data and isinstance(cache_data, dict):
                    cache.delete(cache_data.get("lid"))
            cache.delete(session_id)
            cache.delete(request.COOKIES.get(LoginView.cookie_name))
        except Exception, e:
            Logger.info("delete session error: {}".format(e))
        response = {"code": 0, "msg": "user logout.", "content": ""}
        return my_response(response, callback)

class UpdateView:
    """
        更新用户信息
    """
    @classmethod
    def run(cls, request, param):
        """
        :param request:
        :param param:
        :return:
        """
        Logger.debug("get cmd update usermessage!")
        request_data = get_request_data(request)
        callback = request_data.get("jsoncallback", "")
        if param == "password":
            Logger.debug("update cmd is password!")
            response = cls.update_password(request_data)
        elif param == "message":
            Logger.debug("update cmd is message!")
            response = cls.update_personal_message(request_data)
        elif param == "phone":
            Logger.debug("update cmd is phone!")
            response = cls.update_phone(request_data)
        else:
            Logger.debug("update cmd is wrong: {}!".format(param))
            response = {"code": 4, "msg": "url error！", "content": ""}
        return my_response(response, callback)

    @staticmethod
    def update_phone(request_data):
        """
        :param request_data:
        :return:
        """
        sid = request_data.get("id")
        if sid is None:
            sid = request_data.get("sid")
        if cache.get(sid):
            # cache.delete(sid)
            username = request_data.get("username")
            user = CustomerAccount.objects.filter(username=username).first()
            phone = request_data.get("phone", None)
            if user and len(str(phone)) == 11:
                if user.phone == "":
                    if CustomerAccount.objects.filter(phone=phone).first():
                        return {"code": 2, "msg": "the user's phone number is existed.", "content": ""}
                    user.phone = phone
                    try:
                        user.save()
                    except Exception, e:
                        return {"code": 5, "msg": e, "content": ""}
                    return {"code": 0, "msg": "update phone number successufl.", "content": ""}
                else:
                    return {"code": 3, "msg": "phone number was existed.", "content": ""}
            else:
                return {"code": 2, "msg": "username or phone number is invalid.", "content": ""}
        else:
            return {"code": 1, "msg": "login timeout.", "content": ""}

    @staticmethod
    def update_password(request_data):
        """
        :param request_data:
        :return:
        """
        Logger.debug("update password!")
        password = request_data.get("password", "")
        session_id = request_data.get("sid")
        print "sid", request_data.get("sid")
        Logger.debug("update_password: {}".format(session_id))
        cache_data = cache.get(session_id)
        if cache_data is None:
            username = ""
        else:
            username = cache_data.get("username")
        cache.delete(session_id)
        if password == "":
            return {"code": 2, "msg": "parameters error.", "content": ""}
        if username == "" or username is None:
            return {"code": 1, "msg": "login timeout", "content": ""}
        user = CustomerAccount.objects.filter(username=username)
        response = {}
        if user.count() > 0:
            user = user[0]
            user.password = encrypt_passwd(password)
            user.save()
            Logger.debug("update password success!")
            response = {"code": 0, "msg": "update password successful.", "content": ""}
        else:
            response = {"code": 3, "msg": "the username is invalid.", "content": ""}
        return response

    @staticmethod
    def update_personal_message(request_data):
        """
        :param request_data:
        :return:
        """
        cache_data = cache.get(request_data.get("sid", ""))
        if cache_data is None or (not isinstance(cache_data, dict)):
            return {"code": 1, "msg": "login timeout.", "content": ""}
        username = cache_data.get("username")
        user = CustomerAccount.objects.filter(username=username).select_related("personal_info").first()
        if user is None:
            return {"code": 3, "msg": "the username is invalid.", "content": ""}
        if user.personal_info is None:
            person = PersonalInfo()
        else:
            person = user.personal_info
        gender = request_data.get("gender", "")
        if gender != "":
            person.gender = gender
        real_name = request_data.get("real_name", "")
        if real_name != "":
            person.name = real_name
        birth_date = request_data.get("birth_date", "")
        if birth_date != "" and re.match(r"\d\d\d\d-\d\d-\d\d$", birth_date):
            person.birth_date = birth_date
        nick_name = request_data.get("nick_name", "")
        if nick_name != "":
            person.nick_name = nick_name
        cert_no = request_data.get("cert_no", "")
        if cert_no != "":
            person.cert_no = cert_no
        cert_limit_date = request_data.get("cert_limit_date", "")
        if cert_limit_date != "":
            person.cert_limit_date = cert_limit_date
        avatar_file = request_data.get("avatar", "")
        if avatar_file != "":
            try:
                avatar_file = json.loads(avatar_file)
                person.avatar.delete(save=False)
                file_name = "avatar_{0}{1}.{2}".format(user.username, avatar_file.get("name", ""),
                                                       avatar_file.get("type", "jpg"))
                person.avatar.save(file_name, ContentFile(base64.b64decode(avatar_file.get("content", ""))))
            except Exception, e:
                Logger.error("update persion avatar error: {}".format(e))
        cert_attachment_front = request_data.get("cert_attachment_front", "")
        if cert_attachment_front != "":
            try:
                cert_attachment_front = json.loads(cert_attachment_front)
                person.cert_attachment_front.delete(save=False)
                file_name = "cert_{0}{1}.{2}".format(user.username, cert_attachment_front.get("name", ""),
                                                     cert_attachment_front.get("type", "jpg"))
                person.cert_attachment_front.save(file_name, ContentFile(base64.b64decode(
                    cert_attachment_front.get("content", ""))))
            except Exception, e:
                Logger.error("update persion cert_attachment_front error: {}".format(e))
        cert_attachment_back = request_data.get("cert_attachment_front", "")
        if cert_attachment_back != "":
            try:
                cert_attachment_back = json.loads(cert_attachment_back)
                person.cert_attachment_back.delete(save=False)
                file_name = "cert_{0}{1}.{2}".format(user.username, cert_attachment_back.get("name", ""),
                                                     cert_attachment_back.get("type", "jpg"))
                person.cert_attachment_back.save(file_name, ContentFile(base64.b64decode(
                    cert_attachment_back.get("content", ""))))
            except Exception, e:
                Logger.error("update persion avatar error: {}".format(e))
        person.save()
        if user.personal_info is None:
            user.personal_info = person
            user.save()
        return {"code": 0, "msg": "update personal message successful.", "content": ""}

class QueryView:
    """
        查询用户是否存在
    """
    @classmethod
    def run(cls, request, param):
        """
        :param request:
        :param param:
        :return:
        """
        Logger.debug("get cmd query usermessage!")
        request_data = get_request_data(request)
        callback = request_data.get("jsoncallback", "")
        if "username" == param:
            Logger.debug("get query cmd is username")
            user = cls.query_by_username(request_data)
            if user == -1:
                return my_response({"code": 2, "msg": "username error.", "content": ""}, callback)
        elif "phone" == param:
            Logger.debug("get query cmd is phone")
            user = cls.query_by_phone(request_data)
            if user == -1:
                return my_response({"code": 2, "msg": "phone number error.", "content": ""}, callback)
        elif "email" == param:
            Logger.debug("get query cmd is email")
            user = cls.query_by_email(request_data)
            if user == -1:
                return my_response({"code": 2, "msg": "email error.", "content": ""}, callback)
        elif "all" == param:
            Logger.debug("get query cmd is all")
            return my_response(cls.query_all(request_data))
        else:
            Logger.debug("get query cmd is wrong: {}!".format(param))
            return my_response({"code": 1, "msg": "parameters error.", "content": ""}, callback)
        return cls._judge(user, callback)

    @classmethod
    def query_by_username(cls, request_data):
        """
        :param request_data:
        :return:
        """
        username = request_data.get("username", "")
        if "" == username:
            return -1
        user = CustomerAccount.objects.filter(username=username).first()
        return user

    @classmethod
    def query_by_email(cls, request_data):
        """
        :param request_data:
        :return:
        """
        email = request_data.get("email", "")
        if "" == email or '@' not in email:
            return -1
        user = CustomerAccount.objects.filter(email=email).first()
        return user

    @classmethod
    def query_by_phone(cls, request_data):
        """
        :param request_data:
        :return:
        """
        phone = request_data.get("phone", "")
        if "" == phone or len(str(phone)) != 11:
            return -1
        user = CustomerAccount.objects.filter(phone=phone).first()
        return user

    @staticmethod
    def query_all(request_data):
        """
        :param request_data:
        :return:
        """
        username = request_data.get("username", "")
        session_id = request_data.get("sid", "")
        cache_data = cache.get(session_id)
        if cache_data is None:
            name = ""
        else:
            name = cache_data.get("username")
        if username != name:
            return {"code": 2, "msg": "login timeout or the username is invalid.", "content": ""}
        user = CustomerAccount.objects.filter(username=username).first()
        if user is None:
            return {"code": 2, "msg": "user is not existed.", "content": ""}
        response_data = {"username": user.username, "phone": user.phone, "email": user.email, "role": user.get_role,
                         "uid": user.id, "real_name": None, "gender": None, "birth_date": None, "cert_no": None,
                         "cert_limit_date": None, "avatar": None, "cert_attachment_front": None, "avatar_url": None,
                         "cert_attachment_back": None, "cert_attachment_front_url": None,
                         "cert_attachment_back_url": None}
        if user.personal_info is not None:
            person = user.personal_info
            response_data["real_name"] = person.name
            response_data["gender"] = person.gender
            birth_date = person.birth_date
            if birth_date is not None:
                birth_date = birth_date.isoformat()
            response_data["birth_date"] = birth_date
            response_data["cert_no"] = person.cert_no
            cert_limit_date = person.cert_limit_date
            if cert_limit_date is not None:
                cert_limit_date = cert_limit_date.isoformat()
            response_data["cert_limit_date"] = cert_limit_date
            url_head = settings.SERVER_WEBSITE + settings.MEDIA_URL[1:]
            if person.avatar.name:
                avatar_url = url_head + person.avatar.name
                response_data["avatar_url"] = avatar_url
                response_data["avatar"] = base64.b64encode(person.avatar.read())
                person.avatar.close()
            else:
                response_data["avatar"] = None
            if person.cert_attachment_front.name:
                front_url = url_head + person.cert_attachment_front.name
                response_data["cert_attachment_front_url"] = front_url
                response_data["cert_attachment_front"] = base64.b64encode(person.cert_attachment_front.read())
                person.cert_attachment_front.close()
            else:
                response_data["cert_attachment_front"] = None
            if person.cert_attachment_back.name:
                back_url = url_head + person.cert_attachment_back.name
                response_data["cert_attachment_back_url"] = back_url
                response_data["cert_attachment_back"] = base64.b64encode(person.cert_attachment_back.read())
                person.cert_attachment_back.close()
            else:
                response_data["cert_attachment_back"] = None
        return {"code": 0, "msg": "query message successful.", "content": response_data}

    @staticmethod
    def _judge(user, callback):
        if user is None:
            return my_response({"code": 3, "msg": "未找到该用户！", "content": ""}, callback)
        else:
            return my_response({"code": 0, "msg": "信息已存在！", "content": ""}, callback)


def my_response(response_data, callback=""):
    """
    :param response_data:
    :param callback:
    :return:
    """
    headers = {'Access-Control-Allow-Origin': '*',
               'Access-Control-Allow-Headers': 'Access-Control-Allow-Origin, x-requested-with, content-type'}
    # Logger.info("response data is :{}".format(response_data["msg"]))
    if callback != "":
        response_data["success"] = "true"
        response = HttpResponse("{0}({1});".format(callback, json.dumps(response_data)),
                                content_type="application/json")
    else:
        response = HttpResponse(json.dumps(response_data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Headers"] = "Access-Control-Allow-Origin, x-requested-with, content-type"
    return response

def get_request_data(request):
    """
    :param request:
    :return:
    """
    if request.method == "GET":
        request_data = request.GET
    else:
        request_data = request.POST
    return request_data
