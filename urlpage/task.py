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


current_dic = os.path.dirname(os.path.abspath(__file__))
spellchecker = Hunspell('en_US',hunspell_data_dir=current_dic+'/dic/')
server_dict={}
server_dict_done={}



#kiểm tra từ điển
def test(word):
    return spellchecker.spell(word)


#chuẩn hóa link
def Urls_check(url):
  while('//' in url):
      url=url.replace('//','/')
  if(url[0]=='/'):
    url = url[1:]
  return url


#lấy tất cả trang web trong web vừa quét
def get_all_web_domain(domain,r,user,n,url):
    global server_dict
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

    pattern = re.compile("^"+domain)
    for link in soup.find_all("a", href=pattern):
        if "href" in link.attrs:
          if link.attrs["href"] not in server_dict[user] and link.attrs["href"] not in server_dict_done[user] and link.attrs["href"]!=url:
               server_dict[user].append(link.attrs["href"])
    
    for link in list_url:
        if("//" in link):
           check_domain = urlparse(link).netloc
           if check_domain==urlparse(domain).netloc:
              linka = "http:"+link
              if linka not in server_dict[user] and linka not in server_dict_done[user] and linka!=url:
                server_dict[user].append(linka)
        else:
           linkb = Urls_check(link)
           linka= domain+linkb
           if linka not in server_dict[user] and linka not in server_dict_done[user] and linka!=url:
               server_dict[user].append(linka)


#lấy tất cả trang web trong web vừa quét
def getdomainname(url):
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result

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

def removeatinde(texts,index):
    newstr = texts[:index]+' '+texts[index+1:]
    return newstr

def removeduplicate(x):
  return list(dict.fromkeys(x))

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

def checkWebsite(url,domain_id,userid,n):
     name_array_tag=[]  
     domain_object = Domain.objects.get(id=domain_id)
     # lấy văn bảng từ trang web
     try:
       scraper = cloudscraper.create_scraper()
       r = scraper.get(url,timeout=5)
       if(r.status_code==200):
         get_url = Urlspage.objects.create(name=url,idDomain=domain_object,is_valid=True)
         get_url.save()
         f= open(settings.MEDIA_ROOT+"/doc/"+str(get_url.id)+".txt","a")
         f.write(r.text)
         f.close()
         # lấy tát cả internal website
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
             #,form_pre=lower_array[word].join(',')
           save_word_url= WordUrls.objects.create(idurl=get_url,idword=save_word,form_pre=','.join(lower_array[word]))
           save_word_url.save()
         #image = PIL.Image.open('urlpage/static/website/'+str(get_url.id)+'.png')
         #width, height = image.size
         #size=[width,height]
         
       else:
        if(Urlspage.objects.filter(name=url,idDomain=domain_object).exists()==False):
         get_url = Urlspage.objects.create(name=url,idDomain=domain_object,is_valid=False)
         get_url.save()
        else:
         page = Urlspage.objects.get(name=url,idDomain=domain_object)
         page.is_valid=False
         page.save()

     except Exception as e:
         if(Urlspage.objects.filter(name=url,idDomain=domain_object).exists()==False):
          get_url = Urlspage.objects.create(name=url,idDomain=domain_object,is_valid=False)
          get_url.save()
         else:
          page = Urlspage.objects.get(name=url,idDomain=domain_object)
          page.is_valid=False
          page.save()



     



@shared_task()
def do_task(url,domain_id,userid,n):
    try:
     server_dict[userid]=[]
     server_dict_done[userid]=[]
     server_dict[userid].append(url)
     
     while(len(server_dict_done[userid])<int(n)):
       if(len(server_dict)>0):
          web = server_dict[userid].pop(0)
          process_percent = int(100 * float(len(server_dict_done[userid])) / float(int(n)))
          current_task.update_state(state='PROGRESS',meta={'process_percent': process_percent,'current_web':web})
          checkWebsite(web,domain_id,userid,n)
          domain = Domain.objects.get(id=domain_id)
          page = Urlspage.objects.get(name=web,idDomain=domain)
          page.is_done=True
          page.save()
          server_dict_done[userid].append(web)
       else:
          break    
     domain=Domain.objects.get(id=domain_id)
     domain.isdone=True
     domain.save()
     return {'process_percent': 100}
    except Exception as e: 
      print(e)
