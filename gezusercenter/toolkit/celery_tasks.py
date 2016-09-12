#!-*-encoding: utf-8 -*-
__author__ = 'PD-002'

from celery import task
from django.conf import settings
from django.core.mail import send_mail


@task()
def my_send_mail(subject, message, email):
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], html_message=message, fail_silently=True)
