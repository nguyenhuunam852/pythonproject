
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
from django.conf import settings

current_dic = os.path.dirname(os.path.abspath(__file__))
spellchecker = Hunspell('en_US',hunspell_data_dir=current_dic+'/../urlpage/dic/')

server_dict1=[]
server_dict_done1=[]   

#chuẩn hóa link
def Urls_check(url):
  while('//' in url):
      url=url.replace('//','/')
  if(url[0]=='/'):
    url = url[1:]
  return url


def test(word):
    return spellchecker.spell(word)

def get_all_web_domain(domain,r,user,n,url):
    global server_dict1
    pattern = re.compile("^(/)")
    soup = BeautifulSoup(r.text, 'lxml')
    
 
    list_url = []
    for link in soup.find_all("a", href=pattern):
       if "href" in link.attrs:
         #linkb = Urls_check(link.attrs["href"]+"/")
         #linka= domain+linkb
         list_url.append(link.attrs["href"])
         #if linka not in server_dict[user] and linka not in server_dict_done[user]:
               #server_dict[user].append(linka)

    url_check2 = url.replace("https://","http://")

    pattern = re.compile("^"+domain)
    for link in soup.find_all("a", href=pattern):
        if "href" in link.attrs:
          http_list=[x.replace("https://","http://") for x in server_dict1]
          http_done_list=[x.replace("https://","http://") for x in server_dict_done1]
          url_check = link.attrs["href"].replace("https://","http://")
          if url_check not in http_list and url_check not in http_done_list and url_check!=url_check2:
               server_dict1.append(link.attrs["href"])
    
    for link in list_url:
        if("//" in link):
           check_domain = urlparse(link).netloc
           if check_domain==urlparse(domain).netloc:
              http_list=[x.replace("https://","http://") for x in server_dict1]
              http_done_list=[x.replace("https://","http://") for x in server_dict_done1]
              linka = "http:"+link
              if linka not in http_list and linka not in http_done_list and linka!=url_check2:
                server_dict1.append(linka)
        else:
           linkb = Urls_check(link)
           linka= domain+linkb
           http_list=[x.replace("https://","http://") for x in server_dict1]
           http_done_list=[x.replace("https://","http://") for x in server_dict_done1]
           linkc = linka.replace("https://","http://")
           if linkc not in http_list and linkc not in http_done_list and linkc!=url_check2:
               server_dict1.append(linka)


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
  f= open(settings.MEDIA_ROOT+"/doc/"+str(website_id)+".txt","a")
  f.write(r.text)
  f.close()
  try:
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
  except Exception as e:
    print(e) 

def checkWebsite(url,domain_id,userid,n,reload,server_dict,server_dict_done):
     name_array_tag=[]  
     domain_object = Domain.objects.get(id=domain_id)
     global server_dict1
     global server_dict_done1
     server_dict1=server_dict
     server_dict_done1=server_dict_done
     
     # lấy văn bảng từ trang web
     try:
       scraper = cloudscraper.create_scraper()
       r = scraper.get(url,timeout=5)
       if(r.status_code==200):
         get_url = Urlspage.objects.create(name=url,idDomain=domain_object,is_valid=True)
         get_url.save()
         # lấy tát cả internal website
         if(reload!=1):
            get_all_web_domain(domain_object.name,r,userid,n,url)
         #phân tích từ vựng của trang web
         name_array_tag=dataAnalysist(r,get_url.id,name_array_tag)
         lower_array={}
         for word in name_array_tag:
            if(word.lower() not in lower_array):
              lower_array[word.lower()]=[word]
            else:
              lower_array[word.lower()].append(word)
         
         #lưu từng từ vào database
         for word in lower_array:
           check= Words.objects.filter(name=word).exists()
           if(check==True):
             save_word = Words.objects.get(name=word)
           else:
             suggest = spellchecker.suggest(word)
             save_word = Words.objects.create(name=word,suggestion=",".join(list(suggest)))
             save_word.save()
           save_word_url= WordUrls.objects.create(idurl=get_url,idword=save_word,form_pre=','.join(lower_array[word]))
           save_word_url.save()    
                
       else:
        if(Urlspage.objects.filter(name=url,idDomain=domain_object).exists()==False):
         get_url = Urlspage.objects.create(name=url,idDomain=domain_object,is_valid=False)
         get_url.save()
        else:
         print('Quet 1')
         page = Urlspage.objects.get(name=url,idDomain=domain_object)
         page.is_valid=False
         page.save()

     except Exception as e:
         if(Urlspage.objects.filter(name=url,idDomain=domain_object).exists()==False):
          get_url = Urlspage.objects.create(name=url,idDomain=domain_object,is_valid=False)
          get_url.save()
         else:
          print('Quet 2')
          page = Urlspage.objects.get(name=url,idDomain=domain_object)
          page.is_valid=False
          page.save()
     return server_dict1,server_dict_done1