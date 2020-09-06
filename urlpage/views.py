
from django.shortcuts import render, redirect  
from urlpage.forms import UrlsForm ,UrlsChangeForm 
from urlpage.models import Urlspage
from validator_collection import validators, checkers
from django.http import JsonResponse
from django.core import serializers
import json
import requests

data={
}
# Create your views here.  
def emp(request):  
    if request.is_ajax and request.method == "POST":
        form = UrlsForm(request.POST)  
        if form.is_valid():
            data= form.cleaned_data.get("name")
            if checkers.is_url(data)==True:
                try:  
                  form.save()
                  url = data
                  r = requests.get(url)
                  print(r)
                  data={}
                  data['check']=r.text
                  return JsonResponse(
                      json.dumps(data),
                      safe=False
                  ) 
                except:  
                  pass  
            else:
                print('Sai')
    else:  
        
        form = UrlsForm()  
    return render(request,'home.html',{'form':form})  

def show(request):
    urls = Urlspage.objects.all()
    return render(request,"show.html",{'urls':urls})  
def edit(request, id):  
    url = Urlspage.objects.get(id=id)  
    return render(request,'edit.html', {'url':url})  
def update(request, id):  
    url = Urlspage.objects.get(id=id)  
    form = UrlsChangeForm(request.POST, instance = url)  
    if form.is_valid():  
        form.save()  
        return redirect('/')  
    return render(request, 'edit.html', {'employee': form})  
def delete(request, id):  
    url = Urlspage.objects.get(id=id)  
    url.delete()  
    return redirect("/")  