from django.shortcuts import render
import json
from django.http import JsonResponse,HttpResponse, HttpResponseRedirect
from urlpage.models import WordUrls,Words,Domain
from words_lib.models import Ignore_word_domain,Personal_words
#from words_lib.models import Ignore_word_page
# Create your views here.
def ignore_page(request):
    data={}
    if(request.method == "POST"):
     try:
       id = request.POST.get("id")
       idpage = request.POST.get("idpage")
       word_url = WordUrls.objects.get(idword=id,idurl=idpage)
       word_url.available=False
       word_url.save()
       data='success'
     except:
       data='fail'
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')

def ignore_domain(request):
    data={}
    if(request.method == "POST"):
      try: 
        id = request.POST.get("id")
        idDomain = request.POST.get("idDomain")
        domain = Domain.objects.get(id=idDomain)
        word = Words.objects.get(id=id)
        new_iwd = Ignore_word_domain.objects.create(idurl=domain,idword=word)
        new_iwd.save()
        data='success'
      except Exception as e:
        print(e)
        data='fail'
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')
    
def personal(request):
    data={}
    if(request.method == "POST"):
      try: 
        id = request.POST.get("id")
        word = Words.objects.get(id=id)
        per_word = Personal_words.objects.create(idword=word,iduser=request.user)
        per_word.save()
        data='success'
      except Exception as e:
        print(e)
        data='fail'
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')