import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Chat


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope["user"].is_anonymous:
            self.close()
        self.user = self.scope["user"]
        async_to_sync(self.channel_layer.group_add)("global", self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("global", self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))

    def new_chat(self, event):
        chat = Chat.objects.get(pk=event["chat_pk"])
        if chat.members.filter(pk=self.user.pk).exists():
            self.send(
                text_data=json.dumps(
                    {
                        "command": "add_chat",
                        "name": chat.get_name(self.user),
                        "image_url": chat.get_image(self.user).url,
                    }
                )
            )
