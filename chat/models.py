import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse
from friendship.models import Block


class Chat(models.Model):
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chats")
    created = models.DateTimeField(auto_now_add=True)

    def get_name(self, for_user):
        if hasattr(self, "chatgroup"):
            return self.chatgroup.name
        return self.members.exclude(pk=for_user.pk)[0].username

    def get_image(self, for_user):
        if hasattr(self, "chatgroup"):
            return self.chatgroup.image
        return self.members.exclude(pk=for_user.pk)[0].profile_pic

    def get_detail_url(self, for_user):
        if hasattr(self, "chatgroup"):
            return reverse("chat:chatgroup_detail", args=[self.chatgroup.pk])
        return reverse(
            "users:user_detail", args=[self.members.exclude(pk=for_user.pk)[0].username]
        )

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

    def is_blocked(self, user):
        if hasattr(self, "chatgroup"):
            return False
        other_user = self.members.exclude(pk=user.pk)[0]
        return Block.objects.is_blocked(user, other_user)


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


class ChatGroup(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="chatgroup_images")
    description = models.TextField(max_length=1000, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_chatgroups",
        on_delete=models.CASCADE,
    )
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE)

    def get_ordinary_members(self):
        return self.chat.members.exclude(pk=self.owner.pk)

    def __str__(self):
        return self.name


class ChatGroupInvite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="invites",
        on_delete=models.CASCADE,
    )
    chatgroup = models.ForeignKey(
        ChatGroup,
        related_name="invites",
        on_delete=models.CASCADE,
    )
    uses = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return str(self.id)
