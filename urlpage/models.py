from django.db import models

class Urlspage(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("urls",max_length=200)
    is_valid=models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Words(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("urls",max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WordUrls(models.Model):
    idurl = models.ForeignKey(Urlspage,on_delete=models.CASCADE)
    idword = models.ForeignKey(Words,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
