from django.shortcuts import render, redirect  
from urlpage.forms import UrlsForm ,UrlsChangeForm,DomainsForm
from users.models import Domain_User,Personal_words 
from urlpage.models import Urlspage,WordUrls,Domain,Words
from django.http import JsonResponse,HttpResponse
from bs4 import BeautifulSoup
import json
import re
from mymodule.pic_analyze import Analyze
from django.conf import settings
import os
import PIL #the image library analyze
from urllib.parse import urlparse
from urlpage.task import do_task
from celery.result import AsyncResult
from rest_framework.response import Response
from django.forms.models import model_to_dict
from mymodule.pagi import getpagi

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

def pictureAnalyze(request):
    data={}

    if(request.method == "POST"):
      test = json.loads(request.body.decode('UTF-8'))
      idpage = test["idpage"]
      list_word = WordUrls.objects.filter(idurl=idpage)
      personal_words = Personal_words.objects.filter(iduser=request.user)
      list_person=[x.idword.id for x in personal_words]
      list_word_available = []
      for w in list_word:
        if(w.idword.id not in list_person):
          list_word_available.append(w)

      words=[]
      for w in list_word_available:
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
        except Exception as e:
         print(e)
         file_name='fail.jpeg'
      else:
        file_name=page.piclink
    data['pic']=file_name
    size=[]
    try: 
      image = PIL.Image.open(settings.MEDIA_ROOT+'/picture/'+str(file_name))
      size = [image.width, image.height] 
      data['size']=size
      data['location']=settings.MEDIA_ROOT+'/picture/'
    except Exception as e:
      print('wrong')
    json_data = json.dumps(data)  
    return HttpResponse(json_data, content_type='application/json')

user_source = {}
def checkref(request):
  global user_source
  if(request.method == "GET"):  
    idurl = request.GET.get('idurl', None)
    idword = request.GET.get('idword', None)
    url = Urlspage.objects.get(id=idurl)
    word = Words.objects.get(id=idword).name
    w_url = WordUrls.objects.get(idurl=idurl,idword=idword)  
    f= open(settings.MEDIA_ROOT+"/doc/"+str(url.id)+".txt","r")
    r = f.read()
    f.close()
    soup = BeautifulSoup(r, 'lxml')
    list_form = w_url.form_pre.split(',')
    for w in list_form:
       findtoure = soup.find_all(text = re.compile(r'\b%s\b'%w))
    
       for comment in findtoure:
         fixed_text = comment.replace(w, ' <mark>'+w+'</mark> ')
         comment.replace_with(BeautifulSoup(fixed_text))

    st = soup.prettify()
    if(len(st)>100000):
      user_source[request.user.id]= [url.id,int(len(st)/100000),st]
    else:
      user_source[request.user.id]= [url.id,1,st]
    st = st[0:100000]
    return render(request,'watch.html',{'word':word,'st':st,'id':w_url.id,'sum':user_source[request.user.id][1]})  

  if(request.method == "POST"):  
    index = request.POST.get('index')
    getsum = user_source[request.user.id][1]
    id = user_source[request.user.id][0]
    st = user_source[request.user.id][2]
    lgth = int(index)-1
    plgth = lgth*100000
    if(int(index)<getsum):
        st = st[plgth:plgth+100000]
    if(int(index)==getsum):
        st = st[plgth:]
    data['text'] = st
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')
    
    
  

    


#Hàm cập nhật trạng thái cho process

def poll_state(request):    
    test = json.loads(request.body.decode('UTF-8'))
    pagi = test['pagination']
    idDomain = test['idDomain']
    print(idDomain)
    domain = Domain.objects.get(id=(int(idDomain)))

    pa = (int(pagi)-1)*5
    items = Urlspage.objects.filter(idDomain=int(idDomain)).order_by('-created_at')[pa:pa+5]
    sumofpage= getpagi(Urlspage.objects.filter(idDomain=int(idDomain)),5)
    data={}
    if(str(request.user.id)+"_"+str(idDomain) in user_process):
        data['signal']='Work'
        task = AsyncResult(user_process[str(request.user.id)+"_"+str(idDomain)])
        data = task.result or task.state
        if(isinstance(data,dict)==True):
          if(data['process_percent']==100):
            user_process.pop(str(request.user.id)+"_"+str(idDomain))
    else:
      data['signal'] = 'Wait'
    try:
      data['items']=[model_to_dict(item) for item in items]
    except:
      print('wait')
    if(str(request.user.id)+'_'+str(idDomain) in user_process):
      data['state']='active'
    else:
      data['state']='n-active'
    data['sumofpages']=sumofpage
    data['isdone']=domain.isdone
    return JsonResponse(data,safe=False)

def test(request):
    return render(request,"testwebview.html",{})  


def show(request):
    global user_process
    user_domain=[]
    pagi = request.GET.get('page', None)
    sort_list=[]
    if request.is_ajax and request.method == "POST":
      form = UrlsForm(request.POST)  
      quantity = request.POST.get('quantity')
      if form.is_valid():
           data= form.cleaned_data.get("name")
           domain = getdomainname(data)
           domain_process=Domain.objects.create(name=domain,isdone=False)
           domain_process.save()
           # lưu Domain vào database
           p= Domain_User(idurl=domain_process,iduser=request.user)
           p.save()
           job = do_task.delay(url=data,domain_id=domain_process.id,userid=request.user.id,n=quantity)
           user_process[str(request.user.id)+"_"+str(domain_process.id)]=job.id

      return redirect("/") 

    if(request.user.is_authenticated and request.method == "GET"):
       form = UrlsForm()
       userurl = Domain_User.objects.filter(iduser=request.user.id).values_list('idurl', flat=True)
       listdomain=list(userurl)
       show_list=[]
       for url in listdomain:
         url= Domain.objects.get(id=url)
         user_domain.append(url)
       sort_list= sorted(user_domain,key=lambda x: x.created_at,reverse=True)
       if(pagi==None):
        show_list=sort_list[0:3]
        current= 1
       else:
        pa = (int(pagi)-1)*3
        show_list=sort_list[pa:pa+3]
        current = pagi
      
       page=getpagi(sort_list,3)
       return render(request,"show.html",{'urls':show_list,'form':form,'page':page,'current':current})  
     
    return render(request,"show.html") 

def delete(request, id):  
    url = Domain.objects.get(id=id)  
    url.delete()  
    return redirect("/")  

def get_all_web(request, id):  
    global user_process
    idDomain = id
    domain = Domain.objects.get(id=int(id))
    pa = 0
    items = Urlspage.objects.filter(idDomain=int(idDomain)).order_by('-created_at')[pa:pa+5]
    sumofpage= getpagi(Urlspage.objects.filter(idDomain=int(idDomain)),5)
    data={}
    if(request.user.id in user_process):
        data['signal']='Work'
        task = AsyncResult(user_process[request.user.id])
        data = task.result or task.state
        if(isinstance(data,dict)==True):
          if(data['process_percent']==100):
            user_process.pop(str(request.user.id)+'_'+str(idDomain))
    else:
      data['signal'] = 'Wait'
    try:
      data['items']=[model_to_dict(item) for item in items]
    except:
      print('wait')
    if(str(request.user.id)+'_'+str(idDomain)  in user_process):
      data['state']='active'
    else:
      data['state']='n-active'
    data['sumofpages']=sumofpage
    data['isdone']=domain.isdone
    return JsonResponse(data,safe=False)


def words(request,id):
    pagi = request.GET.get('page', None)
    words = WordUrls.objects.filter(idurl=id)
    personal_words = Personal_words.objects.filter(iduser=request.user)
    list_person=[x.idword.id for x in personal_words]
    list_word = []
    for w in words:
      w.idword.idcommon = w.id
      if(w.idword.id not in list_person):
          list_word.append(w.idword)
    sumofpages = getpagi(list_word,7)
    if(pagi==None):
      pagi=1
    pa = (int(pagi)-1)*7
    list_word_pagi = list_word[pa:pa+7]
    data['items']=[model_to_dict(item) for item in list_word_pagi]
    data['sum']=sumofpages
    return JsonResponse(data,safe=False)

def personal(request):
    data={}
    if(request.method == "POST"):
      try: 
        test = json.loads(request.body.decode('UTF-8'))
        id = test['id']
        word = Words.objects.get(id=id)
        per_word = Personal_words.objects.create(idword=word,iduser=request.user)
        per_word.save()
        data='success'
      except Exception as e:
        print(e)
        data='fail'
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')