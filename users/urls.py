from django.urls import path
from .views import SignUpView
from users import views
from django.views.generic.base import TemplateView
app_name = "userinfo"

urlpatterns = [
    path('/signup/', SignUpView.as_view(), name='signup'),
    path('/login/', views.user_login, name='login'),
    path('/logout/', views.user_logout, name='logout'),
    path('/history', TemplateView.as_view(template_name='wordsview.html'), name='history'),
    path('/getignoreinfor',views.getinfor),
    path('/sigup_user', views.signup, name='newlogin'),
    path('/login_user', views.user_login, name='login'),
]