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

    def __init__(self, *args, **kwargs):
        super(UrlsForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class' : 'form-control','placeholder':'Put Your URL here!'})

class UrlsChangeForm(forms.ModelForm):  
    class Meta:  
        model = Urlspage 
        fields = ('name','is_valid') 

    