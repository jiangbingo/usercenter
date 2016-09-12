# Create your tests here.
from django.contrib import admin

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id','key','name', 'description', 'type','apphandler','argument','create','modified')
    search_fields = ('key','name','description')
admin.site.register(Application,ApplicationAdmin)