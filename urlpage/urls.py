# config/urls.py
from urlpage import views
from django.urls import path  
urlpatterns = [
    path('',views.show),
    path('poll_state',views.poll_state),
    path('add/',views.emp),
    path('gethref/',views.checkref),
    path('getpic/',views.checkpic),
    path('update/<int:id>',views.update),
    path('delete/<int:id>',views.delete),
    path('view/<int:id>',views.get_all_web),
    path('words/<int:id>',views.get_all_word)
]