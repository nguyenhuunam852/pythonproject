from django.shortcuts import render, redirect  
from urlpage.forms import UrlsForm ,UrlsChangeForm 
from urlpage.models import Urlspage
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
spellchecker = hunspell.HunSpell('/usr/share/hunspell/en_GB.dic',
                                 '/usr/share/hunspell/en_GB.aff')
index=0
id_array_tag=[]
name_array_tag=[]
correction={}

def test(word):
    return spellchecker.spell(word)

def getobject(text):
   NNP_name=[]
   list_name=[]
   newString = (text.replace(u'\u200b', ' '))
   doc = nlp(newString)
   for x in doc:
       if(x.ent_type_ == ''):
        text=str(x)
        if(text.isalpha()==True):
          if (text in list_name)==False:
             list_name.append(text)
       else:
        text=str(x)
        if(text.isalpha()==True):
          if (text in NNP_name)==False:
            NNP_name.append(text.lower())
   for w in list_name:
       if w.lower() in NNP_name:  
          list_name.remove(w)
   return list_name

data={
}
save=""

def dataAnalysist(r):
    global name_array_tag
    name_array_tag=[]
    texts=[]
    n_arrays=[]
    w_arrays=[]
    soup = BeautifulSoup(r.text, 'lxml')
    texts = soup.get_text(separator=', ')
    texts= ' '.join(getobject(texts))
    w_arrays=re.split(r"[^a-zA-Z']",texts)

    for w in w_arrays :
        t=str(w)
        for ew in t:
            if(ew.isalnum()==False):
               if w in w_arrays:  
                 w_arrays.remove(w)
    
    for text in w_arrays:
        if(test(text)==False):
          n_arrays.append(text)
         
    name_array_tag=n_arrays
    return soup.prettify()


async def savedata(data,id):
    browser = await launch(
         handleSIGINT=False,
         handleSIGTERM=False,
         handleSIGHUP=False
    )
    page = await browser.newPage()
    await page.goto(data)
    await page.screenshot({'path': 'urlpage/static/website/'+str(id)+'.png','fullPage':'true'})
    await browser.close()
  
  

   
    
# Create your views here.  
def emp(request):  
    if request.is_ajax and request.method == "POST":
        form = UrlsForm(request.POST)  
        if form.is_valid():
            data= form.cleaned_data.get("name")
            if checkers.is_url(data)==True:
                try:  
                 global index
                 index=0
                 global name_array_tag
                 name_array_tag=[]
                 testtype=1
                 if(testtype==1):
                   urlpath=form.save()
                   url = data
                   r = requests.get(url)
                   text=dataAnalysist(r)
                   loop = asyncio.new_event_loop()
                   asyncio.set_event_loop(loop)
                   loop.run_until_complete(savedata(data,urlpath.id))  
                   image = PIL.Image.open('urlpage/static/website/'+str(urlpath.id)+'.png')
                   width, height = image.size
                   size=[width,height]
                   data={}
                   data['check']=text
                   data['tagname']=name_array_tag
                   data['id']=urlpath.id
                   data['size']=size
                   return JsonResponse(
                      json.dumps(data),
                      safe=False
                   ) 
                 else:
                   url = data
                   r = requests.get(url)
                   soup = BeautifulSoup(r.text, 'lxml')
                   texts = soup.get_text(separator=' ')
                   
                   texts= ' '.join(getobject(texts))

                except Exception as e: 
                  print(e)  
            else:
                print('Sai')
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
      if text == word:
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
       comment.replace_with(BeautifulSoup(fixed_text))
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

def deleteAll(request):  
    url = Urlspage.objects.all()
    url.delete()  
    return redirect("/")  

