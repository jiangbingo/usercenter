# -- encoding: utf-8 --
__author__ = 'PD-002'

from django.conf.urls import url
from .user_views import RegisterView, QueryView, UpdateView, LoginView, LogoutView
from .check_views import EmailCheckView, PhoneCheckView, CodeCheckView
from .approve_views import MessageView
from .designer_views import DesignerView
from .user_views import RecodView
from .feedback_views import feed_back
from .other_views import SyncMessage

urlpatterns = [
    # 用户注册
    url(r'^register/$', RegisterView.register, name="register"),
    # 邮箱验证码get/check
    url(r'^emailcheck/(.+)/$', EmailCheckView.run, name="emailcheck"),
    # 短信验证码get/check
    url(r'^phonecheck/(.+)/$', PhoneCheckView.run, name="phonecheck"),
    # 图片验证码get/check
    url(r'^codecheck/(.+)/$', CodeCheckView.run, name='codecheck'),
    # 检测唯一性username/email/phone
    url(r'^query/(.+)/$', QueryView.run, name='query'),
    # 更新 password/email/phone
    url(r'^update/(.+)/$', UpdateView.run, name="update"),
    # 登录
    url(r'^login/$', LoginView.login, name="login"),
    # 获取用户认证状态
    url(r'^get_status/$', LoginView.get_status, name="get_status"),
    # 邮箱验证码验证
    url(r'^ecode_check/$', LoginView.email_code_check, name="email_code_check"),
    # 记录登录记录
    url(r'^set_record/$', RecodView.set_record, name="set_record"),
    # 获取登录记录
    url(r'^get_record/$', RecodView.get_record, name="get_record"),
    # ajax 同步登陆记录
    url(r'^set_cookie/$', RecodView.set_cookie, name="set_cookie"),
    # 登出
    url(r'^logout/$', LogoutView.logout, name="logout"),
    # 用户信息   upload/get
    url(r'^message/(.+)/$', MessageView.run, name="message"),
    # 设计师认证
    url(r'^designer/(.+)/$', DesignerView.run, name="designer"),
    # 用户反馈
    url(r'^feedback/$', feed_back, name="feedback"),
    # 同步第三方用户
    url(r'^other/(.+)/$', SyncMessage.run, name="other"),
]
