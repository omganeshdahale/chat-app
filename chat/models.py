from django.conf import settings
from django.db import models


class Chat(models.Model):
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chats")
    created = models.DateTimeField(auto_now_add=True)

    def get_name(self, for_user):
        return self.members.exclude(pk=for_user.pk)[0].username

    def get_image(self, for_user):
        return self.members.exclude(pk=for_user.pk)[0].profile_pic

    def get_last_message_preview(self, for_user):
        try:
            m = self.messages.latest("created")
        except Message.DoesNotExist:
            return "No last message"
        if m.sender == for_user:
            return f"You: {m.message}"
        return f"{m.sender}: {m.message}"

    def get_unread_messages_count(self, for_user):
        return self.messages.exclude(read_by=for_user).count()

    def get_last_message_or_created_datetime(self):
        try:
            return self.messages.latest("created").created
        except Message.DoesNotExist:
            return self.created

    def is_member(self, user):
        return self.members.filter(pk=user.pk).exists()


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="sent_messages", on_delete=models.CASCADE
    )
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    message = models.CharField(max_length=2000)
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="read_messages"
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def to_dict(self):
        return {
            "author": self.sender.username,
            "author_img_url": self.sender.profile_pic.url,
            "message": self.message,
            "datetime": self.created.isoformat(),
        }

    def __str__(self):
        return f"{self.sender}: {self.message}"
