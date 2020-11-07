# config/urls.py
from urlpage import views
from django.urls import path  
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import TemplateView

urlpatterns = [
    path('',views.show),
    path('poll_state',views.poll_state),
    path('get_words/<int:id>',views.test,name="test"),
    path('gethref/',views.checkref),
    path('analyze_pic',views.pictureAnalyze),
    path('delete/<int:id>',views.delete),
    path('view/<int:id>',views.get_all_web),
    path('words',TemplateView.as_view(template_name='wordsview.html'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)