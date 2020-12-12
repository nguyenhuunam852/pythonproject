
from celery import shared_task,current_task
from bs4 import BeautifulSoup
from urlpage.models import Urlspage
from urlpage.models import Words
from urlpage.models import WordUrls,Domain
import cloudscraper
import urllib
from urllib.parse import urlparse
import re
import PIL
import time
import en_core_web_sm
import os
from mymodule.mongo import checkWord
from django.conf import settings
nlp = en_core_web_sm.load()
from hunspell import Hunspell


#chuẩn hóa văn bản và phân tích tất cả các thành phần dựa trên nlp
def getobject(text):
   NNP_name=[]
   list_name=[]
   n_text = text.split('\n')
   list_m=[]
   for n in n_text:
     m_text = n.split(' ')
     for i,m in enumerate(m_text):
       if('-' in m) or ('_' in m) or ('.' in m) or ("'" in m):
         m_text[i]=''
     list_m.append(' '.join(m_text))
   text='\n'.join(list_m)

   newString = (text.replace(u'\u200b', ' '))
   doc = nlp(newString)  
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
   for w in list_name:
       if w.lower() in NNP_name:  
          list_name.remove(w)
          
   return list_name

def dataAnalysist(r,website_id,name_array_tag):
    texts=[]
    n_arrays=[]
    w_arrays=[]
    new = r.text.replace('/>','>')
    soup = BeautifulSoup(new, 'lxml')
  
    texts = soup.get_text(separator='\n')
    i=0
    texts = texts.replace(u'\u200b', ' ')
    texts= ' '.join(getobject(texts))
    texts = texts.split(' ')
    for i,w in enumerate(texts):
      if(w.encode().isalpha()==False):
        texts[i]=""
    texts = ' '.join(texts)
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
    result_array=[]

    for w in name_array_tag:
       ck = checkWord(w,website_id)
       if(ck>0):
          result_array.append(w)
    #soup.prettify()
    return result_array