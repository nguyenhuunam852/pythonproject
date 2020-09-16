# config/urls.py
from urlpage import views
from django.urls import path  
urlpatterns = [
    path('',views.show),
    path('add/',views.emp),
    path('gethref/',views.checkref),
    path('getpic/',views.checkpic),
    path('edit/<int:id>',views.edit),
    path('update/<int:id>',views.update),
    path('delete/<int:id>',views.delete),
    path('deleteall',views.deleteAll)
]