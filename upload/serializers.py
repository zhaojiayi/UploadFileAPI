from rest_framework import serializers
from .models import UploadFile

class UploadSerializers(serializers.ModelSerializer):
    # touser=serializers.CharField(allow_blank=False,default="@all")
    # toparty=serializers.CharField(allow_blank=False)
    # totag=serializers.CharField(allow_blank=False)
    # file=serializers.FileField(allow_empty_file=False)
    class Meta:
        model=UploadFile
        fields='__all__'
