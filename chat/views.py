from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def chat(request):
    chats = request.user.chats.all()
    return render(request, "chat/chat.html", {"chats": chats})
