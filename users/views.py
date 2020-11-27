from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate,login, logout
from .forms import CustomUserCreationForm,CustomUserLoginForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import Personal_words
from mymodule.pagi import getpagi

    
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

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details given")
    else:
        form_class=CustomUserLoginForm
        return render(request, 'registration/login.html', {'form':form_class})




def ignore_list_history(request):
    pagi = request.GET.get('page', None)
    pa = (int(pagi)-1)*11
    list_words = Personal_words.objects.filter(iduser=request.user.id)
    page = getpagi(list_words,11)
    list_words = list_words.order_by('-created_at')[pa:pa+11]
    current = pagi
    return render(request,'testwebview.html',{'word_list':list_words,'current':current,'page':page})