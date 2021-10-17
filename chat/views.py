from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def chat(request):
    chats = sorted(
        request.user.chats.all(),
        key=lambda c: c.get_last_message_or_created_datetime(),
        reverse=True,
    )
    return render(request, "chat/chat.html", {"chats": chats})
