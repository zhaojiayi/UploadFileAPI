from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.parsers import FileUploadParser,MultiPartParser
import requests
from rest_framework import status
from .models import UploadFile ,Application
from uploadAPI import settings
import os
import threading
import json
from urllib.parse import urlencode



from .serializers import UploadSerializers
# Create your views here.



class UploadView(APIView):
    '''
    File Upload API
    '''
    parser_classes=[MultiPartParser,]

    def post(self, request, *args, **kwargs):
    #     def handle_uploaded_file(f):
    #         with open('./tmp', 'wb+') as destination:
    #             for chunk in f.chunks():
    #                 destination.write(chunk)
        #print(type(request.GET.get('token')))

        #检查token
        res={'errcode':0,'errmsg':'ok'}

        if request.content_type.find("multipart/form-data")==-1:
            res['errcode']=1
            res['errmsg']="invalid content-type(must be multipart/form-data)"
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
        token=request.GET.get('token') #没有token属性返回None

        if token!='123abc':
            res['errcode']=2
            res['errmsg']="invalid token"
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
        ################输出请求体格式###################
        # body=request.body.decode('utf-8','ignore')
        # with open('print1.txt','w',encoding='utf-8') as f:
        #     f.write(body)
        
        ################判断重复文件####################
        # file_path=os.path.join(settings.MEDIA_ROOT,request.META['REMOTE_ADDR'],request.FILES['file'].name)
        # file_path.replace('\\','/')
        # is_find=UploadFile.objects.filter(file=file_path)
        # if(not is_find):
        #     errmsg="duplicate upload"
        #     return Response({"errmsg":errmsg},status=status.HTTP_400_BAD_REQUEST)
        
        
        #反串行化参数到数据库
        request.data['ip']=request.META['REMOTE_ADDR']
        serializer=UploadSerializers(data=request.data)
        if not serializer.is_valid():
            errcode=3
            errmsg="invalid format"
            errors_copy=serializer.errors.copy() #serializer.errors不可修改，copy可以修改
            errors_copy['errcode']=errcode
            errors_copy['errmsg']=errmsg
            errors_copy.move_to_end('errmsg',last=False)#移动到最上面
            errors_copy.move_to_end('errcode',last=False)
            return Response(errors_copy,status=status.HTTP_400_BAD_REQUEST)
        serializer.save()



        # return Response(res,status=status.HTTP_200_OK)


        # print(request.data)
        # print(serializer.validated_data)
        # print(serializer.data)
        # print(type(request.body.decode()))#得到请求体的文本字符串形式


        #print(request.FILES['file'].name)#返回文件名
        #request.FILES['file']的类型是<class 'django.core.files.uploadedfile.InMemoryUploadedFile'>，属于UploadedFile
        ##UploadedFile是属于request.FILES的，FieldFile是属于model的
        #print(request.content_type)
        #print(dir(request.user))  #['check_password', 'delete', 'get_all_permissions', 'get_group_permissions', 'get_username', 'groups', 'has_module_perms', 'has_perm', 'has_perms', 'id', 'is_active', 'is_anonymous', 'is_authenticated', 'is_staff', 'is_superuser', 'pk', 'save', 'set_password', 'user_permissions', 'username']


        # 获取请求的值，并使用对应的JSONParser进行处理
        #print(request.data)#<QueryDict: {'user': ['sdasd'], 'file': [<InMemoryUploadedFile: API.txt (text/plain)>]}>
        
        # application/x-www-form-urlencoded 或 multipart/form-data时，request.POST中才有值
        #print(request.POST)#<QueryDict: {'user': ['sdasd']}>

        #request.FILES     ['appendlist', 'clear', 'copy', 'dict', 'fromkeys', 'get', 'getlist', 'items', 'keys', 'lists', 'pop', 'popitem', 'setdefault', 'setlist', 'setlistdefault', 'update', 'values']

        #request.FILES.['file']      ['charset', 'chunks', 'close', 'closed', 'content_type', 'content_type_extra', 'encoding', 'field_name', 'file', 'fileno', 'flush', 'isatty', 'multiple_chunks', 'name', 'newlines', 'open', 'read', 'readable', 'readinto', 'readline', 'readlines', 'seek', 'seekable', 'size', 'tell', 'truncate', 'writable', 'write', 'writelines']

        #print(dir(request.FILES['file']))
        #handle_uploaded_file(request.FILES['file'])

        #######################重新上传#############################
        final=UploadFile.objects.last()
        f=final.file
        agentid=final.agentid
        from django.core.exceptions import ObjectDoesNotExist
        try:
            app=Application.objects.get(agentid=agentid)
        except ObjectDoesNotExist:
            res['errcode']=4
            res['errmsg']="invalid agentid"
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        corpsecret=app.corpsecret
        ###########################################################
        #corpsecret='B-dx4HjLJ0-bPnCJ7YTrlpJA3WAhlvOi1Iev5bbswMA' #应用凭证密钥
        # agentid='1000002'
        corpid='wwee67915ac292143a' #企业ID
        msgtype='file'
        api_common='https://qyapi.weixin.qq.com/cgi-bin/'
        # url_token=api_common+'gettoken?corpid='+corpid+'&'+'corpsecret='+corpsecret
        url_token=api_common+'gettoken?'+urlencode({'corpid':corpid,'corpsecret':corpsecret})

        #获取access_token
        res_token=requests.get(url_token)
        res_token_dict=res_token.json() #返回字典
        if(res_token_dict['errcode']!=0):
            return Response(res_token_dict,status=status.HTTP_400_BAD_REQUEST)
        access_token=res_token_dict['access_token'] #得到access_token
        url_upload=api_common+'media/upload?'+urlencode({'access_token':access_token,'type':'file'})

        #上传素材得到media_id
        #files={'file':('API.txt',open('./tmp','rb'))}#name和filename需要英文
        
        # print(request.FILES['file'].name)#返回文件名
        # print(request.FILES.getlist('file'))#返回文件名

        filename=request.FILES['file'].name
        filename=filename.replace('"','')#postman测试接口文件名末尾可能会出现双引号
        files={'file':(filename,f.open())}#这个是Uploadedfile的name
        res_upload=requests.post(url_upload,files=files)
        response_upload_dict=res_upload.json() #返回字典
        if(response_upload_dict['errcode']!=0):
            return Response(response_upload_dict,status=status.HTTP_400_BAD_REQUEST)
        media_id=response_upload_dict['media_id']#得到media_id
        file={"media_id":media_id}
        req_file_body={"msgtype":msgtype,"agentid":agentid,"file":file}
        req_file_body.update(request.POST.dict())#加入touser toparty totag
        #print(req_file_body)
        url_send_file=api_common+'message/send?'+urlencode({'access_token':access_token})
        res_file=requests.post(url_send_file,json=req_file_body) #json直接赋值字典
        res_file=res_file.json()
        #####################上传发送成功，更新is_send################
        if(res_file['errcode']==0):
            final.is_send=True
            final.save()
            return Response(res_file,status=status.HTTP_200_OK)
        return Response(res_file,status=status.HTTP_400_BAD_REQUEST)
        # return Response('ok')


def sendfile(upload_id,filename):
    res={}
    final=UploadFile.objects.get(pk=upload_id)
    f=final.file
    to3={'touser':final.touser,'totag':final.totag,'toparty':final.toparty}
    agentid=final.agentid
    from django.core.exceptions import ObjectDoesNotExist
    try:
        app=Application.objects.get(agentid=agentid)
    except ObjectDoesNotExist:
        res['errcode']=4
        res['errmsg']="invalid agentid"
        final.status=json.dumps(res)
        final.save()
    corpsecret=app.corpsecret
    ###########################################################
    #corpsecret='B-dx4HjLJ0-bPnCJ7YTrlpJA3WAhlvOi1Iev5bbswMA' #应用凭证密钥
    # agentid='1000002'
    corpid='wwee67915ac292143a' #企业ID
    msgtype='file'
    api_common='https://qyapi.weixin.qq.com/cgi-bin/'
    url_token=api_common+'gettoken?'+urlencode({'corpid':corpid,'corpsecret':corpsecret})
    #获取access_token
    res_token=requests.get(url_token)
    res_token_dict=res_token.json() #返回字典
    if(res_token_dict['errcode']!=0):
        final.status=json.dumps(res_token_dict)
        final.save()
        return
    access_token=res_token_dict['access_token'] #得到access_token
    url_upload=api_common+'media/upload?'+urlencode({'access_token':access_token,'type':'file'})
    #上传素材得到media_id
    #files={'file':('API.txt',open('./tmp','rb'))}#name和filename需要英文
    
    # print(request.FILES['file'].name)#返回文件名
    # print(request.FILES.getlist('file'))#返回文件名

    files={'file':(filename,f.open())}#filename必须是原始的，不能是Uploadedfile的名字（有后缀）
    res_upload=requests.post(url_upload,files=files)
    response_upload_dict=res_upload.json() #返回字典
    if(response_upload_dict['errcode']!=0):
        final.status=json.dumps(response_upload_dict)
        final.save()
        return
    media_id=response_upload_dict['media_id']#得到media_id
    file={"media_id":media_id}
    req_file_body={"msgtype":msgtype,"agentid":agentid,"file":file}
    req_file_body.update(to3)#加入touser toparty totag
    #print(req_file_body)
    url_send_file=api_common+'message/send?'+urlencode({'access_token':access_token})
    res_file=requests.post(url_send_file,json=req_file_body) #json直接赋值字典
    res_file=res_file.json()
    #####################上传发送成功，更新is_send################
    final.status=json.dumps(res_file)
    # print(type(json.dumps(res_file)))
    final.save()
    if(res_file['errcode']==0):
        final.is_send=True
        final.save()

    parser_classes=[MultiPartParser,]


class UploadAsyView(APIView):
    parser_classes=[MultiPartParser,]

    def post(self, request, *args, **kwargs):


        #检查token
        res={'errcode':0,'errmsg':'upload to server'}
        if request.content_type.find("multipart/form-data")==-1:
            res['errcode']=1
            res['errmsg']="invalid content-type(must be multipart/form-data)"
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
        token=request.GET.get('token') #没有token属性返回None

        if token!='123abc':
            res['errcode']=2
            res['errmsg']="invalid token"
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
        
        
        #反串行化参数到数据库
        #更新方法
        request.data['ip']=request.META['REMOTE_ADDR']
        serializer=UploadSerializers(data=request.data)
        if not serializer.is_valid():
            errcode=3
            errmsg="invalid format"
            errors_copy=serializer.errors.copy() #serializer.errors不可修改，copy可以修改
            errors_copy['errcode']=errcode
            errors_copy['errmsg']=errmsg
            errors_copy.move_to_end('errmsg',last=False)#移动到最上面
            errors_copy.move_to_end('errcode',last=False)
            return Response(errors_copy,status=status.HTTP_400_BAD_REQUEST)
        serializer.validated_data['status']="已上传至服务器，未发送至微信"
        serializer.save()

        upload_id=serializer.data.get('id')
        filename=request.FILES['file'].name
        filename=filename.replace('"','')#postman测试接口文件名末尾可能会出现双引号
        ##########创建线程
        t1=threading.Thread(target=sendfile,args=(upload_id,filename))
        t1.start()
        #要返回id以便查询
        res.update({'uploadid':upload_id})
        return Response(res,status=status.HTTP_200_OK)

class QueryView(APIView):
    
    def get(self,request,id,*args,**kwargs):
        res={'errcode':0,'errmsg':'ok'}
        token=request.GET.get('token') #没有token属性返回None

        if token!='123abc':
            res['errcode']=2
            res['errmsg']="invalid token"
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
        
        from django.core.exceptions import ObjectDoesNotExist
        try:
            re=UploadFile.objects.get(id=id)
        except ObjectDoesNotExist:
            res['errcode']=5
            res['errmsg']="invalid uploadid"
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        #同步上传，默认同步为空，异步状态有上传未发送、已发送后返回微信响应
        try:
            re1=json.loads(re.status)
        except json.decoder.JSONDecodeError:
            st=status.HTTP_400_BAD_REQUEST
            return Response('This file is uploaded synchronously',status=st)
        if re1.get('errcode')==0:
            st=status.HTTP_200_OK
        else:
            st=status.HTTP_400_BAD_REQUEST
        return Response(re1,status=st)