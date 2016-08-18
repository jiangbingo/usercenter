#!-*-encoding: utf-8 -*-
__author__ = 'PD-002'

from .models import CustomerAccount, FeedbackMessage
from .user_views import get_request_data, my_response

def feed_back(request):
    """
    :param request:
    :return:
    """
    request_data = get_request_data(request)
    username = request_data.get("username", "")
    email = request_data.get("email", "")
    phone = request_data.get("phone", "")
    social_no = request_data.get("social_no", "")
    if email == "" and social_no == "" and phone == "":
        return my_response({"code": 1, "msg": "param is lack.", "content": ""})
    message = request_data.get("content", "")
    title = request_data.get("title", "")
    if message == "" and title == "":
        return my_response({"code": 1, "msg": "content is null.", "content": ""})
    feed_message = FeedbackMessage(name=request_data.get("name"), email=email, phone=phone,
                                   social_no=social_no, title=request_data.get("title"), message=message)
    if username != "":
        account = CustomerAccount.objects.filter(username=username).first()
        if account is not None:
            feed_message.account_no = account.account_no
            feed_message.username = account.username
    feed_message.save()
    return my_response({"code": 0, "msg": "feekback successful.", "content": ""})
