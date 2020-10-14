from django.db import models

class Domain(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("domain",max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Urlspage(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("url",max_length=2000)
    is_valid=models.BooleanField(default=True)
    idDomain=models.ForeignKey(Domain,default="",on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Words(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("urls",max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WordUrls(models.Model):
    idurl = models.ForeignKey(Urlspage,on_delete=models.CASCADE)
    idword = models.ForeignKey(Words,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
