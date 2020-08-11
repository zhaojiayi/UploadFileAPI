from django.db import models

# Create your models here.

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/{1}'.format(instance.ip, filename)

class UploadFile(models.Model):
    created_time=models.DateTimeField(auto_now_add=True,editable=True) 
    ip=models.CharField(max_length=20)
    touser=models.CharField(max_length=1000,blank=True)
    toparty=models.CharField(max_length=1000,blank=True)
    totag=models.CharField(max_length=1000,blank=True)
    file=models.FileField(upload_to=user_directory_path)
    is_send=models.BooleanField(default=False)
    # agentid=models.ForeignKey('Application',on_delete=models.CASCADE)
    agentid=models.IntegerField()
    status=models.CharField(max_length=100,blank=True)
    
class Application(models.Model):
    agentid=models.IntegerField(primary_key=True)
    corpsecret=models.CharField(max_length=200)
    
    class Meta:
        managed = True