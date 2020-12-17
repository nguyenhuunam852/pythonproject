from django.db import models
from users.models import CustomUser
import datetime


class Domain(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("domain",max_length=2000)
    isdone=models.BooleanField(default=True)
    iduser = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Urlspage(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("url",max_length=2000)
    is_valid=models.BooleanField(default=True)
    idDomain=models.ForeignKey(Domain,default="",on_delete=models.CASCADE)
    piclink = models.CharField(default="",max_length=2000)
    is_done=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Words(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("urls",max_length=2000)
    suggestion = models.CharField("suggest",default="",max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WordUrls(models.Model):
    id = models.AutoField(primary_key=True)
    idurl = models.ForeignKey(Urlspage,on_delete=models.CASCADE)
    idword = models.ForeignKey(Words,on_delete=models.CASCADE)
    form_pre = models.CharField(default="",max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Personal_words(models.Model):
    id = models.AutoField(primary_key=True)
    iduser = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    idword = models.ForeignKey(Words,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
