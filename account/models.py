from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
import phonenumbers


class MyAccountManager(BaseUserManager):
    def create_user(self, email, first_name, password= None):
        user = self.model(
            email=self.normalize_email(email),
            password=password,
            first_name=first_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            first_name=first_name,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(unique = True)
    first_name = models.CharField(max_length = 20, default = '')
    phone = models.IntegerField(default = '1')
    country = models.CharField(max_length = 50, default = '')
    is_admin = models.BooleanField(default = False)
    is_superuser = models.BooleanField(default = False)
    is_staff = models.BooleanField(default = False)
    is_active = models.BooleanField(default = True)
    subjects = models.TextField(default = '', max_length = 255)
    knowledge = models.TextField(max_length = 200)
    google_link = models.TextField(max_length = 250)
    team = models.TextField(max_length = 250)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True