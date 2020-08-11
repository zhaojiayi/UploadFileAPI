from django.contrib import admin
from .models import UploadFile,Application

class RatingAdmin(admin.ModelAdmin):#让admin显示基于auto_now_add的DateTimeField
    readonly_fields = ('created_time','is_send')

admin.site.register(UploadFile,RatingAdmin)

admin.site.register(Application)
# Register your models here.
