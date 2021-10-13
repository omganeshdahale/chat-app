from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.dispatch import receiver
from friendship.signals import friendship_request_accepted
from .models import Chat


@receiver(friendship_request_accepted)
def create_chat(from_user, to_user, **kwargs):
    if Chat.objects.filter(members=from_user).filter(members=to_user).exists():
        return

    chat = Chat.objects.create()
    chat.members.add(from_user, to_user)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "global", {"type": "new_chat", "chat_pk": chat.pk}
    )
