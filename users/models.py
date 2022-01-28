from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image


class User(AbstractUser):
    profile_pic = models.ImageField(upload_to="profile_pics")
    about_me = models.CharField(max_length=100, default="Available")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.profile_pic:
            img = Image.open(self.profile_pic.path)
            output_size = (96, 96)
            img = img.resize(output_size)
            img.save(self.profile_pic.path)
