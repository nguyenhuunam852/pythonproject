from django.urls import path
from .views import SignUpView
from users import views

app_name = "userinfo"

urlpatterns = [
    path('/signup/', SignUpView.as_view(), name='signup'),
    path('/login/', views.user_login, name='login'),
    path('/logout/', views.user_logout, name='logout'),
    path('/history', views.ignore_list_history, name='history'),
    path('/sigup_user', views.signup, name='newlogin'),
    path('/login_user', views.user_login, name='login'),
]