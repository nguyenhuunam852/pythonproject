from django import template
from django.utils.html import conditional_escape
register = template.Library()
from django.utils.safestring import mark_safe
@register.filter()
def replace_text(value):
    i=0
    k=len(value)
    while(i<k):
        if(value[i]=='<'):
            print(value[i+1:i+5])
            if(value[i+1:i+5]!='mark' and value[i+1:i+6]!='/mark'):
              value=value.replace(value[i],'&lt;',1)
            else:
              value=value.replace(value[i],'<',1)

        i+=1
        k=len(value)
    
            
              
   
    return mark_safe(value) 
   
