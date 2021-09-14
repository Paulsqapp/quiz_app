from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
# Create your models here.
class User(AbstractUser):
    pass

    def __str__(self): # i was overriding this method with pass
        return f"{self.username}"
        

    class Meta:
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUsers'
