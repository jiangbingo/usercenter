#!-*-encoding: utf-8 -*-
__author__ = 'PD-002'
try:
    import simplejson as json
except:
    import json
import base64
import random
import time
import urllib
import urllib2
import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from toolkit.createimgcode import CreateImgCode
from toolkit.mylogger import Logger

from .models import CustomerAccount
from .user_views import get_request_data, my_response


class EmailCheckView:
    """
        验证邮箱有效性
    """

    server_check_url = settings.SERVER_WEBSITE + "usermanager/emailcheck/check/"
    server_recheck_url = settings.SERVER_WEBSITE + "usermanager/emailcheck/recheck/"
    # 邮箱校验链接超时时间
    session_timeout = 3600 * 24
    # 发送邮件间隔
    post_email_interval = 60
    login_url = settings.OFFICIAL_WEBSITE + "home/successfulActivation/"
    update_password_url = settings.OFFICIAL_WEBSITE + "home/resetPwd"
    # client_url = settings.OFFICIAL_WEBSITE + "home/tempPage"

    @classmethod
    def run(cls, request, param):
        Logger.debug("get cmd emailcheck")
        request_data = get_request_data(request)
        if "get" == param:
            Logger.debug("emailcheck cmd is get!")
            return cls.post_email_check_link(request_data)
        elif "check" == param:
            Logger.debug("emailcheck cmd is check!")
            return cls.email_check(request_data)
        elif "reget" == param:
            Logger.debug("emailcheck cmd is reget!")
            return cls.repost_email_check_link(request_data)
        elif "recheck" == param:
            Logger.debug("emailcheck cmd is jump!")
            return cls.jp_update(request_data)
        else:
            Logger.debug("emailcheck cmd is wrong: {}!".format(param))
            return HttpResponse(json.dumps({"code": 2, "msg": "parameters error.", "content": ""}))

    # 发送密码修改验证链接
    @classmethod
    def repost_email_check_link(cls, request_data):
        """
        :param request_data:
        :return:
        """
        email = request_data.get("email", "")
        callback = request_data.get("jsoncallback", "")
        if email == "" or '@' not in email:
            return my_response({"code": 1, "msg": "email invalid.", "content": ""}, callback)
        user = CustomerAccount.objects.filter(email=email).first()
        if user:
            username = user.username
            subject = '密码重置链接'
            token = uuid.uuid4().get_hex()
            content = '{0}?sid={1}'.format(cls.server_recheck_url, token)
            tm = time.localtime()
            stm = "{0}年{1}月{2}日".format(tm.tm_year, tm.tm_mon, tm.tm_mday)
            html_message = '<!DOCTYPE html><html><head></head><body><b>亲爱的用户：</b>\
                <br />您好！感谢您使用空间艺术！您正在进行修改密码操作，请点击下方链接来修改您的密码: \
                <br /><a href="{0}">{1}</a><br />为了确保您的账号安全，该链接仅24小时内访问有效并点击一次后失效！\
                <br />若点击链接不工作,请您复制链接至浏览器窗口地址栏中，并点击Enter键。<br /> <br />\
                空间艺术<br />{2}</body></html>'.format(content, content, stm)
            cache.set(token + "email_update_password", request_data.get("url"), timeout=EmailCheckView.session_timeout)
            response = cls._post_mail(email, subject, html_message, token, username)
        else:
            response = {"code": 5, "msg": "email error.", "content": ""}
        return my_response(response, callback)

    # 密码修改验证链接验证
    @staticmethod
    def jp_update(request_data):
        """
        :param request_data:
        :return:
        """
        session_id = request_data.get("sid", "")
        if session_id == "":
            return HttpResponse("错误请求！")
        cache_data = cache.get(session_id, "")
        if cache_data != "":
            username = cache_data.get("username")
        else:
            username = None
        cache.delete(session_id)
        if username is None:
            return HttpResponse("该验证链接已过期，请重新申请！")
        else:
            token = uuid.uuid4().get_hex()
            old_token = session_id + "email_update_password"
            url = cache.get(old_token)
            cache.delete(old_token)
            cache.set(token, {"username": username}, timeout=EmailCheckView.session_timeout)
            if url is None:
                return HttpResponseRedirect(EmailCheckView.update_password_url + "?id=" + token)
            else:
                return HttpResponseRedirect(url + "?id=" + token)

    # 发送邮箱有效性认证链接
    @classmethod
    def post_email_check_link(cls, request_data):
        """
        :param request_data:
        :return:
        """
        email = request_data.get("email", "")
        username = request_data.get("username", "")
        callback = request_data.get("jsoncallback", "")
        # if email == "" and username != '':
        #     user = CustomerAccount.objects.filter(username=username).first()
        #     if user:
        #         email = user.email
        if email == "" or '@' not in email:
            Logger.info("email error，email :{0}".format(email))
            return my_response({"code": 1, "msg": "email invalid.", "content": ""}, callback)
        user = CustomerAccount.objects.filter(email=email).first()
        if user is None:
            return my_response({"code": 1, "msg": "email error.", "content": ""}, callback)
        if username != "" and username != user.username:
            return my_response({"code": 5, "msg": "username, email does not match.", "content": ""}, callback)
        else:
            username = user.username
        subject = '激活链接'
        source = request_data.get("source", "")
        if source == "designer":
            source_msg = '计师平台（<a href="{0}">{0}</a>）'.format(settings.DESIGNER_WEBSITE,
                                                              settings.DESIGNER_WEBSITE)
            # source = 0
        else:
            source_msg = '官网（<a href="{0}">{0}</a>）'.format(settings.OFFICIAL_WEBSITE, settings.OFFICIAL_WEBSITE)
            # source = 1
        token = uuid.uuid4().get_hex()
        # content = '{0}?sid={1}'.format(cls.server_check_url, token)
        content = "".join(random.sample(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], 6))
        print "code", content
        tm = time.localtime()
        stm = "{0}年{1}月{2}日".format(tm.tm_year, tm.tm_mon, tm.tm_mday)
        # html_message = '<!DOCTYPE html><html><head></head><body><b>亲爱的用户：</b>\
        #             <br />您好！感谢您使用格菱网络科技有限公司服务，您正在进行{0}的账号激活操作，\
        #             请点击下方链接来激活您的账号: <br /><a href="{1}">{2}</a><br />为了确保您的账号安全，\
        #             该链接仅24小时内访问有效并点击一次后失效！<br />若点击链接不工作,\
        #             请您复制链接至浏览器窗口地址栏中，并点击Enter键。<br /> <br />\
        #             格菱网络科技有限公司<br />{3}</body></html>'.format(source_msg, content, content, stm)
        html_message = '<!DOCTYPE html><html><head></head><body><b>亲爱的用户：</b>\
                    <br />您好！感谢您使用空间艺术！您正在进行{0}<br />的账号激活操作，\
                    请在登录界面通过此验证码来激活您的账号: <a href="{1}">{2}</a><br />为了确保您的账号安全，\
                    该验证码仅5分钟内输入有效并验证成功后失效！<br /> <br />\
                    空间艺术<br />{3}</body></html>'.format(source_msg, "", content, stm)
        cache.set(token + "email_check", request_data.get("url"), timeout=PhoneCheckView.note_timeout)
        response = cls._post_mail(email, subject, html_message, token, username, content)
        return my_response(response, callback)

    @staticmethod
    def _post_mail(email, subject, message, token, username="", source=0):
        """
        :param email:
        :param subject:
        :param message:
        :param token:
        :param username:
        :return:
        """
        try:
            old_token = cache.get(email)
            if old_token:
                cache.delete(old_token)
                cache.delete(email)
            if cache.get("check" + email):
                return {"code": 4, "msg": "request too frequently.", "content": ""}
            else:
                if source != 0:
                    cache.set("ecode" + username, source, timeout=300)
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email], html_message=message, fail_silently=True)
                cache.set("check" + email, True, timeout=EmailCheckView.post_email_interval)
                cache.set(email, token, timeout=EmailCheckView.session_timeout)
                cache.set(token, {"username": username, "source": source}, timeout=EmailCheckView.session_timeout)
                return {"code": 0, "msg": "send email successful.", "content": ""}
        except Exception, e:
            Logger.error("send email check link error: {}".format(e))
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], html_message=message, fail_silently=True)
            return {"code": 3, "msg": "network exception，send email failed.", "content": ""}

    # 邮箱验证
    @staticmethod
    def email_check(request_data):
        """
        :param request_data:
        :return:
        """
        session_id = request_data.get("sid", "")
        if session_id == "":
            return HttpResponse("wrong request.")
        cache_data = cache.get(session_id)
        username = False
        source = 0
        if cache_data is not None:
            username = cache_data.get("username")
            source = cache_data.get("source", 0)
        cache.delete(session_id)
        if not username:
            return HttpResponse("该验证链接已过期，请重新申请！")
        user = CustomerAccount.objects.filter(username=username).first()
        if user:
            user.email_certified = True
            user.save()
            old_token = session_id + "email_check"
            url = cache.get(old_token)
            cache.delete(old_token)
            token = uuid.uuid4().get_hex()
            cache.set(token, {"username": username}, timeout=3600 * 2)
            un = urllib.quote(base64.b64encode(username))
            param_url = "?sid={0}&un={1}&login=0&uid={2}&username={3}&source={4}&nflag=0".format(token, un, user.id,
                                                                                                 un, source)
            if url is None:
                return HttpResponseRedirect(EmailCheckView.login_url + param_url)
            else:
                return HttpResponseRedirect(url + param_url)
        else:
            return HttpResponse("验证失败，请联系管理员！")

class CodeCheckView:
    """
        图片验证码
    """
    session_timeout = 62

    @classmethod
    def run(cls, request, param):
        """
        :param request:
        :param param:
        :return:
        """
        Logger.debug("get cmd codecheck!")
        request_data = get_request_data(request)
        if "get" == param:
            Logger.debug("codecheck cmd is get!")
            return cls._post_img_check_code(request_data)
        elif "check" == param:
            Logger.debug("codecheck cmd is check!")
            return cls._img_code_check(request_data)
        else:
            Logger.debug("codecheck cmd is wrong: {}!".format(param))
            return HttpResponse(json.dumps({"code": 1, "msg": "parameters error.", "content": ""}))

    # 获取图片校验码
    @staticmethod
    def _post_img_check_code(request_data):
        username = request_data.get("username", "")
        callback = request_data.get("jsoncallback", "")
        if username == "":
            return my_response({"code": 1, "msg": "username is null.", "content": ""}, callback)
        which = uuid.uuid4().get_hex()
        name, img_data = CreateImgCode().get_code_picture()
        content = {"img_data": img_data, "id": which, "format": CreateImgCode.ft}
        response_data = {
            "code": 0,
            "content": content,
            "msg": "image checkcode create successful."}
        cache.set(which, name, timeout=CodeCheckView.session_timeout)
        return my_response(response_data, callback)

    @staticmethod
    def _img_code_check(request_data):
        which = str(request_data.get("id"))
        code = request_data.get("code")
        callback = request_data.get("jsoncallback", "")
        if not which or not code:
            return my_response({"code": 3, "msg": "parameters error.", "content": ""}, callback)
        real_code = cache.get(which, "")
        if "" == real_code:
            return my_response({"code": 2, "msg": "checkcode timeout.", "content": ""}, callback)
        if real_code.lower() == code.lower():
            return my_response({"code": 0, "msg": "checkcode correct.", "content": ""}, callback)
        else:
            return my_response({"code": 1, "msg": "checkcode invalid.", "content": ""}, callback)

class PhoneCheckView:
    """
        手机号码有效性验证
    """

    url = "http://sdk2.entinfo.cn:8061/mdsmssend.ashx?sn=SDK-WSS-010-09551&pwd=679422DB127555AD14D1A861D9FEF371&ext=&stime=&msgfmt="
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # 短信验证码的超时时间
    note_timeout = 300
    # 短信发送间隔时间
    note_fre_timeout = 50
    # 短信网关的超时时间
    post_note_timeout = 30

    @classmethod
    def run(cls, request, param):
        """
        :param request
        :param param
        :param return
        """
        Logger.debug("get cmd phonecheck!")
        request_data = get_request_data(request)
        callback = request_data.get("jsoncallback", "")
        if param == "get":
            Logger.debug("phonecheck cmd is get!")
            response = cls._post_note_check_code(request_data)
        elif param == "check":
            Logger.debug("phonecheck cmd is check!")
            response = cls._note_code_check(request_data)
        else:
            Logger.info("phonecheck cmd is wrong: {}!".format(param))
            response = {"code": 3, "msg": "url error！", "content": ""}
        return my_response(response, callback)

    # 发送手机验证码
    @staticmethod
    def _post_note_check_code(request_data):
        phone = request_data.get("phone", "")
        username = request_data.get("username", "")
        if phone == "" or len(phone) != 11 or not phone.isdigit():
            Logger.debug("post note code parameters error, phone is invalid.")
            return {"code": 1, "msg": "parameters error, phone is invalid.", "content": ""}
        if cache.get(phone) is not None:
            Logger.debug("post note code request too frequency.")
            return {"code": 2, "msg": "request too frequency.", "content": ""}
        if username == "":
            user = CustomerAccount.objects.filter(phone=phone).first()
            if user is None:
                Logger.debug("the phone number is not registed.")
                return {"code": 3, "msg": "the phone number is not registed.", "content": ""}
            username = user.username
        else:
            user = CustomerAccount.objects.filter(username=username).first()
            if user is None:
                return {"code": 3, "msg": "username is invalid.", "content": ""}
        purpose = request_data.get("purpose", "")
        if purpose == "update":
            purpose_msg = "您正在进行找回密码操作"
        else:
            purpose_msg = "您正在进行手机绑定操作"
        sid = uuid.uuid4().get_hex()
        rand_code = "".join(random.sample(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], 6))
        rrid = str(int(time.time()*1000))
        content = "【空间艺术】 验证码是{0}，{1}，验证码5分钟内有效，并输入一次后作废".format(
            rand_code, purpose_msg)
        content = urllib.quote(content)
        url = "{0}&mobile={1}&content={2}&rrid={3}".format(PhoneCheckView.url, phone, content, rrid)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req, timeout=PhoneCheckView.post_note_timeout)
        if response.code != 200:
            Logger.error("network error: {}".format(response.code))
            return {"code": 2, "msg": "short message gateway error, send message error.", "content": ""}
        if response.read() == rrid:
            cache.set(sid, {"code": rand_code, "username": username}, timeout=PhoneCheckView.note_timeout)
            cache.set(phone, True, timeout=PhoneCheckView.note_fre_timeout)
            return {"code": 0, "msg": "send message successful.", "content": {"id": sid}}
        else:
            Logger.error("return rrid is not equal to rrid!::{}".format(response.read()))
            return {"code": 2, "msg": "send message failed.", "content": ""}

    # 校验手机验证码
    @staticmethod
    def _note_code_check(request_data):
        sid = request_data.get("id", "")
        code = request_data.get("code", "")
        # username = request_data.get("username", "")
        if sid == "" or code == "":
            return {"code": 1, "msg": "parameters error.", "content": ""}
        cache_data = cache.get(sid)
        if cache_data is None:
            return {"code": 3, "msg": "checkcode timeout", "content": ""}
        real_code = cache_data.get("code")
        if real_code == code:
            cache.delete(sid)
            token_for_update_passwd = uuid.uuid4().get_hex()
            cache.set(token_for_update_passwd, {"username": cache_data.get("username")},
                      timeout=PhoneCheckView.note_timeout)
            return {"code": 0, "msg": "note checkcode check successful.", "content": {"id": token_for_update_passwd}}
        else:
            return {"code": 2, "msg": "note checkcode check failed.", "content": ""}
