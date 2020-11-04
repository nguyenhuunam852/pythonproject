from django import template
from django.utils.html import conditional_escape
register = template.Library()
from django.utils.safestring import mark_safe

@register.filter(name='times') 
def times(number):
    return range(1,number+1)