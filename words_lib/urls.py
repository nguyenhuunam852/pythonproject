from django.urls import path
from words_lib import views

urlpatterns = [
    path('/ignore_page', views.ignore_page, name='page'),
    path('/ignore_domain', views.ignore_domain, name='domain'),
    path('/personal', views.personal, name='domain')
]