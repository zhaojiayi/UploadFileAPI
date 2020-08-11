from django.conf.urls import url
from upload import views

urlpatterns=[
    # url(r'^(?P<token>\w+)$',views.UploadView.as_view(),name='upload'),
    #尽量用正则，防止截胡
    url(r'^upload/$',views.UploadView.as_view()),
    url(r'^asyupload/$',views.UploadAsyView.as_view()),
    url(r'^asyupload/(?P<id>[0-9]+)/$',views.QueryView.as_view()),

]