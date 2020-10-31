# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', include('urlpage.urls'), name='home'),
    path('ignore',include('words_lib.urls'),name='ignore'),
    path('account', include('users.urls'), name='acount')
]
