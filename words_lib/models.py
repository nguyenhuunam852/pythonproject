from django.db import models
from urlpage.models import Urlspage,Words,Domain
from users.models import CustomUser 

# Create your models here.

class Ignore_word_domain(models.Model):
    id = models.AutoField(primary_key=True)
    idurl = models.ForeignKey(Domain,on_delete=models.CASCADE)
    idword = models.ForeignKey(Words,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Personal_words(models.Model):
    id = models.AutoField(primary_key=True)
    iduser = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    idword = models.ForeignKey(Words,on_delete=models.CASCADE)

