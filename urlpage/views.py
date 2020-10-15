from django.shortcuts import render, redirect  
from urlpage.forms import UrlsForm ,UrlsChangeForm 
from users.models import Url_User 
from urlpage.models import Urlspage,WordUrls
from validator_collection import validators, checkers
from django.http import JsonResponse
from django.core import serializers
from bs4 import BeautifulSoup
import json
import requests
import hunspell
import re
import nltk 
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import os 
from nltk.chunk import tree2conlltags
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from html import unescape
nlp = en_core_web_sm.load()
import asyncio
from pyppeteer import launch
import pytesseract
import cv2
import os
from pytesseract import Output
import PIL
from users.models import Url_User
from django.views.decorators.csrf import csrf_exempt
import urllib.parse
from urllib.parse import urlparse
spellchecker = hunspell.HunSpell('/usr/share/hunspell/en_GB.dic',
                                 '/usr/share/hunspell/en_GB.aff')
index=0
id_array_tag=[]

correction={}
def getdomainname(url):
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result
def test(word):
    return spellchecker.spell(word)

def getobject(text):
   NNP_name=[]
   list_name=[]
   newString = (text.replace(u'\u200b', ' '))
   doc = nlp(newString)
   print(doc)
   for x in doc:
       if(x.ent_type_ == ''):
        text=str(x)
        if(text=="n't"):
             list_name.pop()
             continue
        if(text.isalpha()==True):
          if (text in list_name)==False:
             list_name.append(text)
       else:
        text=str(x)
        if(text.isalpha()==True):
          if (text in NNP_name)==False:
            NNP_name.append(text.lower())
   print(NNP_name)
   for w in list_name:
       if w.lower() in NNP_name:  
          list_name.remove(w)
   return list_name

data={
}
save=""
server_dict={

}
server_dict_done={

}
user_domain={

}
def removeatinde(texts,index):
    newstr = texts[:index] + texts[index+1:]
    return newstr

def dataAnalysist(r,name_array_tag):
    texts=[]
    n_arrays=[]
    w_arrays=[]
    soup = BeautifulSoup(r.text, 'lxml')
    texts = soup.get_text(separator='\n')
    i=0
    n=len(texts)
    while i < n-11:
        if(texts[i]=='\n'):
            if(texts[i+1].isalpha()==True and texts[i+1].islower()==True):
                texts=removeatinde(texts,i)
                n=len(texts)

        i+=1
    
    print(texts)
    texts= ' '.join(getobject(texts))
    w_arrays=re.split(r"[^a-zA-Z']",texts)

    for w in w_arrays :
        t=str(w)
        for ew in t:
            if(ew.isalnum()==False):
               if w in w_arrays:  
                 w_arrays.remove(w)
    
    for text in w_arrays:
        print(text)
        if(test(text)==False):
          n_arrays.append(text)
         
    name_array_tag=n_arrays

    return soup.prettify(),name_array_tag



def savedata(data,id):
   
  BASE = 'https://mini.s-shot.ru/1024x0/PNG/1024/Z100/?' # you can modify size, format, zoom
  url = data
  url = urllib.parse.quote_plus(url) #service needs link to be joined in encoded format


  path = 'urlpage/static/website/'+str(id)+'.png'
  response = requests.get(BASE + url, stream=True)

  if response.status_code == 200:
    with open(path, 'wb') as file:
        for chunk in response:
            file.write(chunk)

def get_all_domain(r,user):
    global server_dict
    global server_dict_done
    global user_domain
    pattern = re.compile("^(/)")
    soup = BeautifulSoup(r.text, 'lxml')

    for link in soup.find_all("a", href=pattern):
       if "href" in link.attrs:
         linka=user_domain[user]+'/'+link.attrs["href"]
         if linka not in server_dict[user] and linka not in server_dict_done[user]:
               new_page = link.attrs["href"]
               server_dict[user].append(user_domain[user]+'/'+new_page)

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
        data['continue']=0
        server_dict_done[request.user.id].append(server_dict[request.user.id].pop(0))
     return data
    except Exception as e: 
      print(e)

# Create your views here.  
def emp(request):  
    global server_dict
    global server_dict_done
    global user_domain
    if request.is_ajax and request.method == "POST":
      if('continue' not in request.POST):
        form = UrlsForm(request.POST)  
        if form.is_valid():
            data= form.cleaned_data.get("name")
            server_dict[request.user.id]=[data]
            server_dict_done[request.user.id]=[]
            user_domain[request.user.id]=getdomainname(data)
            if checkers.is_url(data)==True:
                try:             
                 urlpath=form.save()
                 data=checkWebsite(urlpath,request)
                 return JsonResponse(json.dumps(data),safe=False) 
                except Exception as e: 
                    print(e)
                    data={}
                    data['error']=1
                    if(len(server_dict)==0):
                     data['continue']=0
                    else:
                     data['next']=server_dict[request.user.id][1]
                     data['continue']=1
                    server_dict_done[request.user.id].append(server_dict[request.user.id].pop(0))
                    return JsonResponse(
                     json.dumps(data),
                     safe=False
                    ) 
                 

            else:
                print('Sai')
      else:
       try:
        data=server_dict[request.user.id][0]
        urlpath= Urlspage(name=data)
        urlpath.save()
        return JsonResponse(json.dumps(checkWebsite(urlpath,request)),safe=False) 
       except Exception as e: 
            print(e)
            data={}
            data['error']=1
            if(len(server_dict)==0):
                     data['continue']=0
            else:
                     data['next']=server_dict[request.user.id][0]
                     data['continue']=1
            server_dict_done[request.user.id].append(server_dict[request.user.id].pop(0))
            return JsonResponse(
                     json.dumps(data),
                     safe=False
                    ) 
                 

    else:  
        form = UrlsForm()  
    return render(request,'home.html',{'form':form})  

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

def checkref(request):
    id = request.GET.get('id', None)
    word = request.GET.get('word', None)
    form = Urlspage.objects.get(id=id)
    r = requests.get(form.name)
    soup = BeautifulSoup(r.text, 'lxml')
    findtoure = soup.find_all(text = re.compile(r'\b%s\b'%word))
    
    for comment in findtoure:
       fixed_text = comment.replace(word, ' <mark>'+word+'</mark> ')
       comment.replace_with(BeautifulSoup(fixed_text),"lxml")
    st = soup.prettify()
    return render(request,'watch.html',{'id':id,'word':word,'st':st})  

def checkpic(request):
    id = request.GET.get('id', None)
    word = request.GET.get('word', None)
    filename=id+word+'.png'
    if(os.path.isfile('urlpage/static/website/'+filename)==False):
      loca= analystPicture(id,word)
    
    return render(request,'picture.html',{'id':id,'word':word,'loca':loca})  

def show(request):
    user_url=[]
    if(request.user.is_authenticated):
      userurl=Url_User.objects.filter(iduser=request.user.id).values_list('idurl', flat=True)
      listurl=list(userurl)
      for url in listurl:
        url=Urlspage.objects.get(id=url)
        user_url.append(url)
    return render(request,"show.html",{'urls':user_url})  

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

def deleteAll(request):  
    url = Urlspage.objects.all()
    url.delete()  
    return redirect("/")  

