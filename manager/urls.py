# config/urls.py
from manager import views
from django.urls import path  
from django.views.generic.base import TemplateView

urlpatterns = [
    path('/get_usersinfor',views.get_users,name="words"),
    path('/deadactive',views.deadactive,name="deadactive"),
    path('/active',views.active,name="active"),
    path('/manageuser',TemplateView.as_view(template_name='manageusers.html')),
    path('/adduser',views.adduser,name="adduser"),
    path('/manageword',TemplateView.as_view(template_name='managewords.html')),
    path('/get_libinfor',views.get_lib),
    path('/uploadfile',views.uploadfile),


]