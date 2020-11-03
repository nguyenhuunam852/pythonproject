from django import forms  
from urlpage.models import Urlspage,Domain

class DomainsForm(forms.ModelForm):  
    class Meta:  
        model = Domain
        fields = ('name',) 

class UrlsForm(forms.ModelForm):  
    class Meta:  
        model = Urlspage 
        fields = ('name',) 

class UrlsChangeForm(forms.ModelForm):  
    class Meta:  
        model = Urlspage 
        fields = ('name','is_valid') 

    