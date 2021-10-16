import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from .models import Chat, Message


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

        if text_data_json["command"] == "send_message":
            self.send_message(text_data_json["chat_pk"], text_data_json["message"])
        elif text_data_json["command"] == "read_messages":
            self.read_messages(text_data_json["chat_pk"])
        elif text_data_json["command"] == "fetch_messages":
            self.fetch_messages(text_data_json["chat_pk"])

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
        chat = Chat.objects.get(pk=event["chat_pk"])
        event["command"] = "new_message"
        event["unread_messages_count"] = chat.get_unread_messages_count(self.user)
        self.send(text_data=json.dumps(event))

    def send_message(self, chat_pk, message):
        chat = Chat.objects.get(pk=chat_pk)
        if chat.is_member(self.user):
            m = Message.objects.create(sender=self.user, chat=chat, message=message)
            async_to_sync(self.channel_layer.group_send)(
                f"chat_{chat.pk}",
                {
                    "type": "new_message",
                    "chat_pk": chat.pk,
                    "author": self.user.username,
                    "author_img_url": self.user.profile_pic.url,
                    "datetime": m.created.isoformat(),
                    "message": message,
                },
            )

    def read_messages(self, chat_pk):
        chat = Chat.objects.get(pk=chat_pk)
        if chat.is_member(self.user):
            messages = chat.messages.exclude(read_by=self.user)
            for message in messages:
                message.read_by.add(self.user)

    def fetch_messages(self, chat_pk):
        chat = Chat.objects.get(pk=chat_pk)
        if chat.is_member(self.user):
            messages = chat.messages.all()
            text_data = {
                "command": "fetched_messages",
                "chat_pk": chat.pk,
                "name": chat.get_name(self.user),
                "image_url": chat.get_image(self.user).url,
                "messages": [m.to_dict() for m in messages],
            }
            self.send(text_data=json.dumps(text_data))
