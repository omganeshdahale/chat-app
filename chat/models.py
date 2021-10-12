from django.conf import settings
from django.db import models


class Chat(models.Model):
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chats")

    def get_name(self, for_user):
        return self.members.exclude(pk=for_user.pk)[0].username

    def get_image(self, for_user):
        return self.members.exclude(pk=for_user.pk)[0].profile_pic


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="messages", on_delete=models.CASCADE
    )
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message = models.CharField(max_length=2000)

    def __str__(self):
        return f"{self.sender}: {self.message}"
