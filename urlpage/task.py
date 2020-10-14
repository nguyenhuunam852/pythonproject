from celery import shared_task,current_task
from numpy import random
from scipy.fftpack import fft
from bs4 import BeautifulSoup
from users.models import Domain_User
from urlpage.models import Urlspage
from urlpage.models import Words
from urlpage.models import WordUrls,Domain
import requests
import urllib
from urllib.parse import urlparse
import re
import PIL
import en_core_web_sm
from celery.contrib import rdb
nlp = en_core_web_sm.load()
from hunspell import Hunspell
spellchecker = Hunspell('en_US')

server_dict={}
server_dict_done={}
#lưu hình ảnh
def savedata(data,id):
   
  BASE = 'https://mini.s-shot.ru/1024x0/PNG/400/Z100/?' # you can modify size, format, zoom
  url = data
  url = urllib.parse.quote_plus(url) #service needs link to be joined in encoded format


  path = 'urlpage/static/website/'+str(id)+'.png'
  response = requests.get(BASE + url, stream=True)

  if response.status_code == 200:
    with open(path, 'wb') as file:
        for chunk in response:
            file.write(chunk)


#kiểm tra từ điển
def test(word):
    return spellchecker.spell(word)

#lấy tất cả trang web trong web vừa quét
def get_all_web_domain(domain,r,user):
    global server_dict
    pattern = re.compile("^(/)")
    soup = BeautifulSoup(r.text, 'lxml')

    for link in soup.find_all("a", href=pattern):
       if "href" in link.attrs:
         linka= domain+'/'+link.attrs["href"]
         if linka not in server_dict[user] and len(server_dict[user])<=3 and linka not in server_dict_done[user]:
               new_page = link.attrs["href"]
               server_dict[user].append(domain+'/'+new_page)

#lấy tất cả trang web trong web vừa quét
def getdomainname(url):
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result


#chuẩn hóa văn bản và phân tích tất cả các thành phần dựa trên nlp
def getobject(text):
   NNP_name=[]
   list_name=[]
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


def dataAnalysist(r,name_array_tag):
    texts=[]
    n_arrays=[]
    w_arrays=[]
    soup = BeautifulSoup(r.text, 'lxml')
    texts = soup.get_text(separator='\n')
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
    #soup.prettify()
    return name_array_tag

def checkWebsite(url,domain_id,userid):
     name_array_tag=[]  
     domain_object = Domain.objects.get(id=domain_id)
     get_url = Urlspage.objects.create(name=url,idDomain=domain_object)
     get_url.save()
     # lấy văn bảng từ trang web
     r = requests.get(url, timeout=5)
     # lấy tát cả internal website
     get_all_web_domain(domain_object.name,r,userid)
     #phân tích từ vựng của trang web
     name_array_tag=dataAnalysist(r,name_array_tag)
     #lưu từng từ vào database
     for word in name_array_tag:
       check= Words.objects.filter(name=word).exists()
       if(check==True):
         save_word = Words.objects.get(name=word)
       else:
         save_word = Words.objects.create(name=word)
         save_word.save()
       save_word_url= WordUrls.objects.create(idurl=get_url,idword=save_word)
       save_word_url.save()
     #lưu hình ảnh trang web
     savedata(url,get_url.id)
     #image = PIL.Image.open('urlpage/static/website/'+str(get_url.id)+'.png')
     #width, height = image.size
     #size=[width,height]

     



@shared_task
def do_task(url,domain_id,userid):
    try:
     server_dict[userid]=[]
     server_dict_done[userid]=[]
     server_dict[userid].append(url)
    
     while(len(server_dict_done[userid])<=3):
          web = server_dict[userid].pop()
          process_percent = int(100 * float(len(server_dict_done[userid])) / float(3))
          current_task.update_state(state='PROGRESS',meta={'process_percent': process_percent,'current_web':web})
          checkWebsite(web,domain_id,userid)
          server_dict_done[userid].append(web)

     return {'process_percent': process_percent,'current_web':web}

     """
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
     """
    except Exception as e: 
      print(e)
