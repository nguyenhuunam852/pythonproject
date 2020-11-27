from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from urlpage.models import Domain,Words
import django.contrib.auth.password_validation as validators
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    def create_user_admin(self,email,password):
        if not email:
            raise ValueError(_('The Email must be set'))
        self.email = email
        try:
          validators.validate_password(password=password)
        except Exception as e:
          print(e)
          return (1999,'PasswordFail')
        self.set_password(password)
        self.is_staff = True
        self.save()
        return self
    def __str__(self):
        return self.email

class Domain_User(models.Model):
    idurl = models.ForeignKey(Domain,on_delete=models.CASCADE)
    iduser = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    

class Personal_words(models.Model):
    id = models.AutoField(primary_key=True)
    iduser = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    idword = models.ForeignKey(Words,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)






