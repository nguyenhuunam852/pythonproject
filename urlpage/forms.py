from django import forms  
from urlpage.models import Urlspage  

class UrlsForm(forms.ModelForm):  
    class Meta:  
        model = Urlspage 
        fields = ('name',) 
class UrlsChangeForm(forms.ModelForm):  
    class Meta:  
        model = Urlspage 
        fields = ('name','is_valid') 

    