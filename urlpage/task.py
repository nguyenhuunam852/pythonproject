from celery import shared_task,current_task
from urlpage.models import Urlspage
from urlpage.models import Words
from urlpage.models import WordUrls,Domain

from mymodule.webAnalyze import checkWebsite

server_dict={}
server_dict_done={}     
current_web={}
current_percent={}
current_domain={}
current_user={}

@shared_task()
def do_task(url,domain_id,userid,n):
    global server_dict
    global server_dict_done
    global current_domain
    global current_user
    try:
     process_id = str(userid)+"_"+str(domain_id)
     server_dict[process_id]=[]
     server_dict_done[process_id]=[]
     current_domain[process_id]=domain_id
     current_user[process_id]=userid
     server_dict[process_id].append(url)
     
     while(len(server_dict_done[process_id])<int(n)):
       if(len(server_dict[process_id])>0):
         try:
          web = server_dict[process_id].pop(0)
          process_percent = int(100 * float(len(server_dict_done[process_id])) / float(int(n)))
          current_task.update_state(state='PROGRESS',meta={'process_percent': process_percent,'current_web':web})
          temp,temp1 = checkWebsite(web,current_domain[process_id],current_user[process_id],n,0,server_dict[process_id],server_dict_done[process_id])
          server_dict[process_id]=temp
          server_dict_done[process_id]=temp1
          domain = Domain.objects.get(id=current_domain[process_id])
          page = Urlspage.objects.get(name=web,idDomain=domain)
          page.is_done=True
          page.save()
          server_dict_done[process_id].append(web)
         except Exception as e: 
            print(e)
       else:
          break    
     domain=Domain.objects.get(id=domain_id)
     domain.isdone=True
     domain.save()
     return {'process_percent': 100}
    except Exception as e: 
      print(e)
