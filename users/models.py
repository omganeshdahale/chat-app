from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    profile_pic = models.ImageField(upload_to="profile_pics")
    about_me = models.CharField(max_length=100, default="Available")
