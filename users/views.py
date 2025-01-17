from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate,login, logout
from .forms import CustomUserCreationForm,CustomUserLoginForm
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from urlpage.models import Personal_words,Words
from mymodule.pagi import getpagi
from django.shortcuts import render, redirect  
import json
from django.forms.models import model_to_dict

from users.models import CustomUser
@login_required
def special(request):
    return HttpResponse("You are logged in !")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('userinfo:login')
    template_name = 'signup.html'

def signup(request):
    data={}
    jsonpost = json.loads(request.body.decode('UTF-8'))
    user = jsonpost['user']
    try:
      User = CustomUser()
      user = User.create_user(user['gmail'],user['password'])
      if(type(user) is tuple):
        if(user[0]==1999):
          data['signal']='password'
      else:
        data['signal']='success'

    except Exception as e:
      print(e)
      if(e.args[0]==1062):
        data['signal']='duplicate'
    print(data)
    return JsonResponse(data,safe=False)

def user_login(request):
    data={}
    if request.method == 'POST':
        jsonpost = json.loads(request.body.decode('UTF-8'))
        user = jsonpost['user']

        user = authenticate(username=user['gmail'], password=user['password'])
        if user:
            if user.is_active:
                login(request,user)
                data['signal']='success'
                return JsonResponse(data,safe=False)
            else:
                data['signal']='n-active'
                return JsonResponse(data,safe=False)
        else:
            data['signal']='fail'
            return JsonResponse(data,safe=False)
    else:
        form_class=CustomUserLoginForm
        return render(request, 'login.html', {'form':form_class})

def getinfor(request):
    data={}
    pagi = request.GET.get('page', None)
    pa = (int(pagi)-1)*11
    list_words = Personal_words.objects.filter(iduser=request.user.id).order_by('-created_at')[pa:pa+11]
    alist = []
    verifylist=[]
    for w in list_words:
        word_infor={}
        word_infor['word']=model_to_dict(w.idword)
        word_infor['verify']=str(w.created_at.hour)+":"+str(w.created_at.minute)+" "+str(w.created_at.day)+"/"+str(w.created_at.month)+"/"+str(w.created_at.year)
        alist.append(word_infor)
    data['items'] = alist
    data['sumofpages'] = getpagi(list_words,11)
    return JsonResponse(data,safe=False)

def removeword(request):
    data={}
    try:
     jsonpost = json.loads(request.body.decode('UTF-8'))
     idword = jsonpost["idword"]
     word = Personal_words.objects.get(idword=idword)
     word.delete()
     data['signal']='done'
    except Exception as e:
     data['signal']='fail'
    return JsonResponse(data,safe=False)
