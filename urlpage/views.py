from django.shortcuts import render, redirect  
from urlpage.forms import UrlsForm ,UrlsChangeForm,DomainsForm
from users.models import Domain_User 
from urlpage.models import Urlspage,WordUrls,Domain,Words
from validator_collection import validators, checkers
from django.http import JsonResponse,HttpResponse, HttpResponseRedirect
from django.core import serializers
from bs4 import BeautifulSoup
import json
import requests
import hunspell
import re
import spacy
from spacy import displacy
from mymodule.pic_analyze import Analyze
from html import unescape
from django.conf import settings
import asyncio
from pyppeteer import launch
import pytesseract
import cv2
import os
from pytesseract import Output
import PIL
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse
from hunspell import Hunspell
from urlpage.task import do_task
from celery.result import AsyncResult
from words_lib.models import Ignore_word_domain,Personal_words


index=0
id_array_tag=[]
data={}
save=""

server_dict_done={}
user_domain={}
correction={}
user_process={}

def getdomainname(url):
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result

"""
def checkWebsite(urlpath,request):
    try:
     name_array_tag=[]   
     global server_dict
     global server_dict_done
     global user_domain
     url = urlpath.name
     p=Url_User(idurl=urlpath,iduser=request.user)
     p.save()
     r = requests.get(url, timeout=5)
     get_all_domain(r,request.user.id)
     text,name_array_tag=dataAnalysist(r,name_array_tag)
     savedata(url,urlpath.id)
     image = PIL.Image.open('urlpage/static/website/'+str(urlpath.id)+'.png')
     width, height = image.size
     size=[width,height]
     data={}
     data['check']=text
     data['tagname']=name_array_tag
     data['id']=urlpath.id
     data['size']=size
     data['error']=0
     if(len(server_dict)==0):
        data['continue']=0
     else:
        data['next']=server_dict[request.user.id][1]                     
        data['continue']=1
        server_dict_done[request.user.id].append(server_dict[request.user.id].pop(0))
     return data
    except Exception as e: 
      print(e)
"""

#Another process
def analystPicture(id,word):
    loca=[]
    img=cv2.imread('urlpage/static/website/'+str(id)+'.png')
    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang='eng')
    n_boxes = len(d['level'])
    overlay = img.copy()
    for i in range(n_boxes):
      text = d['text'][i]
      if word in text:
        (x1, y1, w1, h1) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        loca.append([x1, y1, w1, h1])
        cv2.rectangle(overlay, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), -1)
    alpha = 0.4  # Transparency factor.
    img_new = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
    picurl=str(id)+word+'.png'
    filename=picurl.format(os.getpid())
    cv2.imwrite("urlpage/static/website/"+filename,img_new)
    return loca

def pictureAnalyze(request):
    data={}
    if(request.method == "POST"):
      idpage = request.POST.get("idpage")
      list_word = WordUrls.objects.filter(idurl=idpage)
      words=[]
      for w in list_word:
        for w1 in w.form_pre.split(','):
          words.append(w1)
      page = Urlspage.objects.get(id=idpage)
      check = page.piclink
      file_name=""
      if (check==""):
        try: 
         pic = Analyze(page,words)
         file_name = os.path.basename(pic)
         page.piclink = file_name
         page.save()
        except:
         file_name='fail.jpeg'
    else:
        file_name=page.piclink
    data['pic']=file_name
    size=[]
    image = PIL.Image.open(settings.MEDIA_ROOT+'/picture/'+str(file_name))
    size = [image.width, image.height] 
    data['size']=size
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')

def checkref(request):
    idurl = request.GET.get('idurl', None)
    idword = request.GET.get('idword', None)
    url = Urlspage.objects.get(id=idurl)
    word = Words.objects.get(id=idword).name
    w_url = WordUrls.objects.get(idurl=idurl,idword=idword)  
    r = requests.get(url.name)
    soup = BeautifulSoup(r.text, 'lxml')
    list_form = w_url.form_pre.split(',')
    for w in list_form:
       findtoure = soup.find_all(text = re.compile(r'\b%s\b'%w))
    
       for comment in findtoure:
         fixed_text = comment.replace(w, ' <mark>'+w+'</mark> ')
         comment.replace_with(BeautifulSoup(fixed_text))

    st = soup.prettify()
    return render(request,'watch.html',{'word':word,'st':st,'id':w_url.id})  

def checkpic(request):
    id = request.GET.get('id', None)
    word = request.GET.get('word', None)
    filename=id+word+'.png'
    if(os.path.isfile('urlpage/static/website/'+filename)==False):
      loca= analystPicture(id,word)
    return render(request,'picture.html',{'id':id,'word':word,'loca':loca})  

#Hàm cập nhật trạng thái cho process
def poll_state(request):
    data = 'Wait'
    if(request.user.id in user_process):
      if request.is_ajax():
          task = AsyncResult(user_process[request.user.id])
          data = task.result or task.state
          if(isinstance(data,dict)==True):
             if(data['process_percent']==100):
               user_process.pop(request.user.id)
      else:
        data = 'This is not an ajax request'
    else:
      data = 'Wait'
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')

def show(request):
    global user_process
    user_domain=[]
    json_data={}
    if request.is_ajax and request.method == "POST":
      form = UrlsForm(request.POST)  
      quantity = request.POST.get('quantity')
      if form.is_valid():
           data= form.cleaned_data.get("name")
           domain = getdomainname(data)
           domain_process=Domain.objects.create(name=domain)
           domain_process.save()
           # lưu Domain vào database
           p= Domain_User(idurl=domain_process,iduser=request.user)
           p.save()
           job = do_task.delay(url=data,domain_id=domain_process.id,userid=request.user.id,n=quantity)
           user_process[request.user.id]=job.id
           json_data['domain']=domain

      json_data['done']=1
      res = json.dumps(json_data)
      return JsonResponse(res, safe=False) 

    if(request.user.is_authenticated and request.method == "GET"):
      if((request.user.id in user_process)==False):
       form = UrlsForm()
       userurl = Domain_User.objects.filter(iduser=request.user.id).values_list('idurl', flat=True)
       listdomain=list(userurl)
       for url in listdomain:
         url= Domain.objects.get(id=url)
         user_domain.append(url)
       return render(request,"show.html",{'urls':user_domain,'form':form})  
      else:
       process_state= AsyncResult(user_process[request.user.id])
       data = process_state.result or process_state.state
       context={
         'urls':user_domain,
         'state':data,
       }
       return render(request,"show.html",context)
    return render(request,"show.html") 

def delete(request, id):  
    url = Domain.objects.get(id=id)  
    url.delete()  
    return redirect("/")  

def get_all_web(request, id):  
    url = Urlspage.objects.filter(idDomain=id)  
    list_url = url
    return render(request, 'webview.html', {'list_url': list_url})  

def get_all_word(request, id):  
    url = Urlspage.objects.get(id=id)
    words = WordUrls.objects.filter(idurl=id,available=True)  
    ignore_domain = Ignore_word_domain.objects.filter(idurl=url.idDomain.id)
    personal_words = Personal_words.objects.filter(iduser=request.user)
    list_ignore=[x.idword.id for x in ignore_domain]
    list_person=[x.idword.id for x in personal_words]
    list_word = []
    for w in words:
      w.idword.idcommon = w.id
      if(w.idword.id not in list_ignore):
        if(w.idword.id not in list_person):
          list_word.append(w.idword)
    if(len(list_word)>0):
      return render(request, 'wordsview.html', {'list_word': list_word,'url':url})  
    else:
      return render(request, 'no_word_view.html', {})  

