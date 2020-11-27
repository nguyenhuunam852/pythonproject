# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', include('urlpage.urls'), name='home'),
    path('account', include('users.urls'), name='acount'),
    path('admin', include('manager.urls'), name='admin')
]
