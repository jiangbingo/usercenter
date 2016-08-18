from django.db import models

# Create your models here.


class SdkKey(models.Model):
    name = models.CharField(max_length=200, default='', null=False)
    domain = models.CharField(max_length=200, default='', null=False)
    token = models.CharField(max_length=200, default='', null=False)
    access_key = models.CharField(max_length=100, default='', null=False)
    secret_key = models.CharField(max_length=100, default='', null=False)
    status = models.IntegerField(default=0, null=False)
    create_time = models.IntegerField(default=0, null=False)
    update_time = models.IntegerField(default=0, null=False)

    class Meta:
        db_table = 'sdk_sdkkey'