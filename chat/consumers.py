import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from .models import Chat


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope["user"].is_anonymous:
            self.close()
        self.user = self.scope["user"]
        async_to_sync(self.channel_layer.group_add)("global", self.channel_name)

        for chat in self.user.chats.all():
            async_to_sync(self.channel_layer.group_add)(
                f"chat_{chat.pk}", self.channel_name
            )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("global", self.channel_name)
        for chat in self.user.chats.all():
            async_to_sync(self.channel_layer.group_discard)(
                f"chat_{chat.pk}", self.channel_name
            )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        chat = Chat.objects.get(pk=text_data_json["chat_pk"])
        if chat.members.filter(pk=self.user.pk).exists():
            message = text_data_json["message"]
            now = timezone.now()

            async_to_sync(self.channel_layer.group_send)(
                f"chat_{chat.pk}",
                {
                    "type": "new_message",
                    "chat_pk": chat.pk,
                    "author": self.user.username,
                    "author_img_url": self.user.profile_pic.url,
                    "datetime": now.isoformat(),
                    "message": message,
                },
            )

    def new_chat(self, event):
        chat = Chat.objects.get(pk=event["chat_pk"])
        if chat.members.filter(pk=self.user.pk).exists():
            async_to_sync(self.channel_layer.group_add)(
                f"chat_{chat.pk}", self.channel_name
            )
            self.send(
                text_data=json.dumps(
                    {
                        "command": "add_chat",
                        "chat_pk": chat.pk,
                        "name": chat.get_name(self.user),
                        "image_url": chat.get_image(self.user).url,
                    }
                )
            )

    def new_message(self, event):
        event["command"] = "new_message"
        self.send(text_data=json.dumps(event))
