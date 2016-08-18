#!-*-encoding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Province(models.Model):
    class Meta:
        # 指定表名
        db_table = 'property_province'
    name = models.CharField(max_length=50, default=None, blank=True, null=True)
    fullname = models.CharField(max_length=50, default=None, blank=True, null=True)
    area_code = models.IntegerField(default=0)
    pinyin = models.CharField(max_length=50, default=None, blank=True, null=True)
    location_lat = models.DecimalField(max_digits=20, decimal_places=10)
    location_lng = models.DecimalField(max_digits=20, decimal_places=10)

    def __unicode__(self):
        return self.fullname


class City(models.Model):
    class Meta:
        # 指定表名
        db_table = 'property_city'
    province = models.ForeignKey('Province', related_name='cities')
    name = models.CharField(max_length=50, default=None, blank=True, null=True)
    fullname = models.CharField(max_length=50, default=None, blank=True, null=True)
    area_code = models.IntegerField(default=0)
    pinyin = models.CharField(max_length=50, default=None, blank=True, null=True)
    location_lat = models.DecimalField(max_digits=20, decimal_places=10)
    location_lng = models.DecimalField(max_digits=20, decimal_places=10)
    post_code = models.CharField(max_length=50, default=None, blank=True, null=True)
    phone_code = models.CharField(max_length=50, default=None, blank=True, null=True)

    def __unicode__(self):
        return self.fullname


class Area(models.Model):
    class Meta:
        # 指定表名
        db_table = 'property_area'
    city = models.ForeignKey('City', related_name='areas')
    fullname = models.CharField(max_length=50, default=None, blank=True,
                                null=True)
    area_code = models.IntegerField(default=0)
    location_lat = models.DecimalField(max_digits=20, decimal_places=10)
    location_lng = models.DecimalField(max_digits=20, decimal_places=10)

    def __unicode__(self):
        return self.fullname