from django.db import models
from users.models import CustomUser
from urlpage.models import Urlspage
class Library_Words(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("name",max_length=100,unique=True)
    iduser = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Library_Words_Web(models.Model):
    id = models.AutoField(primary_key=True)
    id_libword = models.ForeignKey(Library_Words,on_delete=models.CASCADE)
    id_web = models.ForeignKey(Urlspage,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)