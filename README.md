# UploadFileAPI
基于Django REST Framework实现同步和异步文件上传发送的API开发；请求和响应均符合RESTful规范。文件上传保存至本地，并调用企业微信接口实现企业内部文件发送

1、token设置为123abc，同步请求url为http://localhost:8000/upload/?token=123abc
异步请求url为http://localhost:8000/asyupload/?token=123abc

2、POST请求格式包含5个参数
```JSON
{
   "touser" : "UserID1|UserID2|UserID3", 
   "toparty" : "PartyID1|PartyID2", 
   "totag" : "TagID1 | TagID2", 
   "agentid" : "...", 
   "file" : "..." 
}
```
3、5个请求参数+IP地址+创建时间+文件描述一起保存到数据库。文件保存在本地files/ip/

4、同步返回参数。如果是微信接口问题，直接返回微信接口的返回参数；如果是开发接口这边的问题（比如token不正确，请求类型不正确等），返回这边相应的参数。
比如发送成功返回：
```JSON
{
    "errcode": 0,
    "errmsg": "ok",
    "invaliduser": ""
}
```
token不正确返回
```JSON
{
    "errcode": 2,
    "errmsg": "invalid token"
}
```

5、异步返回参数。返回文件id供调用查询状态接口。
例如上传成功后返回
```JSON
{
    "errcode": 0,
    "errmsg": "upload to server",
    "uploadid": 132
}
```
6、异步查询url为http://localhost:8000/asyupload/(id)/?token=123abc
