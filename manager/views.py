
from django.shortcuts import render, redirect 
from users.models import CustomUser 
from manager.models import Library_Words
from django.forms.models import model_to_dict
import json
from django.http import JsonResponse,HttpResponse
from mymodule.pagi import getpagi
import pandas as pd

# Create your views here.
def get_users(request):
    data={}
    pagi = request.GET.get('page', None)    
    plot = (int(pagi)-1)*6
    items = CustomUser.objects.all().order_by('-date_joined')[plot:plot+6].only('id','email','date_joined','is_active','is_staff')
    all_items = list(CustomUser.objects.all())

    data['items']=[model_to_dict(item) for item in items]
    data['sumofpages']=getpagi(all_items,6)
    return JsonResponse(data,safe=False)

def get_lib(request):
    data={}
    pagi = request.GET.get('page', None)    
    plot = (int(pagi)-1)*6
    items = Library_Words.objects.all().order_by('name')[plot:plot+6].only('id','name','iduser','created_at')
    all_items = list(Library_Words.objects.all())

    items=[model_to_dict(item,fields=['id','name','iduser']) for item in items]
    for item in items:
      user = Library_Words.objects.get(id=item['id'])
      item['created_at']=str(user.created_at.date())
      item['f_user']=model_to_dict(CustomUser.objects.get(id=item['iduser']))
    data['items']=items
    data['sumofpages']=getpagi(all_items,6)
    return JsonResponse(data,safe=False)

def uploadfile(request):
    data={}
    read = pd.read_csv(request.FILES['myFile'])
    list_word = read['name'].values[0::]
    for word in list_word:
      try:
       if(Library_Words.objects.filter(name=word).exists()==False): 
         new_word = Library_Words.objects.create(name=word,iduser=request.user)
      except Exception as e:
       print(e)
       data['signal']='Fail'
    if('signal' not in data):
      data['signal']='Success'
    return JsonResponse(data,safe=False)


def deadactive(request):
    data={}
    jsonpost = json.loads(request.body.decode('UTF-8'))
    id = jsonpost['id']
    try:
      user = CustomUser.objects.get(id=id)
      user.is_active = False
      user.save()
      data['signal']='success'
    except Exception as e:
      print(e)
      data['signal']='fail'
    return JsonResponse(data,safe=False)

def active(request):
    data={}
    jsonpost = json.loads(request.body.decode('UTF-8'))
    id = jsonpost['id']

    try:
      user = CustomUser.objects.get(id=id)
      user.is_active = True
      user.save()
      data['signal']='success'

    except Exception as e:
      print(e)
      data['signal']='fail'
    return JsonResponse(data,safe=False)



def adduser(request):
    data={}
    jsonpost = json.loads(request.body.decode('UTF-8'))
    if('iduser' not in jsonpost):
     user = jsonpost['user']
     
     try:
      User = CustomUser()
      user = User.create_user_admin(user['gmail'],user['password'])
      if(type(user) is tuple):
        if(user[0]==1999):
          data['signal']='password'
      else:
        data['signal']='success'

     except Exception as e:
      print(e)
      if(e.args[0]==1062):
        data['signal']='duplicate'

    else:
      iduser = jsonpost['iduser']
      
      user = CustomUser.objects.get(id=iduser)
      user = user.setpassword(jsonpost['user'])
      if(type(user) is tuple):
          if(user[0]==1999):
           data['signal']='password'
      else:
          data['signal']='success'

    return JsonResponse(data,safe=False)

