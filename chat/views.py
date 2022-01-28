from io import BytesIO
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core import files
from django.core.exceptions import PermissionDenied
from django.db.models import F
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
import requests
from .forms import ChatGroupCreateForm, ChatGroupUpdateForm
from .models import Chat, ChatGroup, ChatGroupInvite

User = get_user_model()


@login_required
def chat(request):
    chats = sorted(
        request.user.chats.all(),
        key=lambda c: c.get_last_message_or_created_datetime(),
        reverse=True,
    )
    return render(request, "chat/chat.html", {"chats": chats})


@login_required
def chatgroup_detail(request, pk):
    chatgroup = get_object_or_404(ChatGroup, pk=pk)
    if not chatgroup.chat.is_member(request.user):
        raise PermissionDenied()

    return render(request, "chat/chatgroup_detail.html", {"chatgroup": chatgroup})


@login_required
def chatgroup_create(request):
    if request.method == "POST":
        form = ChatGroupCreateForm(request.POST, request.FILES)
        if form.is_valid():
            chatgroup = form.save(commit=False)
            chatgroup.owner = request.user
            chat = Chat.objects.create()
            chat.members.add(request.user)
            chatgroup.chat = chat
            if not chatgroup.image:
                url = f"https://ui-avatars.com/api/?name={chatgroup.name}&size=96&bold=true&background=random"
                response = requests.get(url)
                fp = BytesIO()
                fp.write(response.content)
                chatgroup.image.save(f"chatgroup_image.png", files.File(fp))
            chatgroup.save()
            messages.success(request, "chat group created")
            return redirect("chat:chatgroup_detail", pk=chatgroup.pk)
    else:
        form = ChatGroupCreateForm()

    return render(request, "chat/chatgroup_create.html", {"form": form})


@login_required
def chatgroup_edit(request, pk):
    chatgroup = get_object_or_404(ChatGroup, pk=pk)
    if request.user != chatgroup.owner:
        raise PermissionDenied()

    if request.method == "POST":
        form = ChatGroupUpdateForm(request.POST, request.FILES, instance=chatgroup)
        if form.is_valid():
            form.save()
            messages.success(request, "chat group saved")
            return redirect("chat:chatgroup_detail", pk=pk)
    else:
        form = ChatGroupUpdateForm(instance=chatgroup)

    context = {
        "chatgroup": chatgroup,
        "form": form,
    }
    return render(request, "chat/chatgroup_edit.html", context)


@require_POST
@login_required
def chatgroup_delete(request, pk):
    chatgroup = get_object_or_404(ChatGroup, pk=pk)
    if request.user != chatgroup.owner:
        raise PermissionDenied()
    chatgroup.chat.delete()
    return redirect("chat:chat")


@require_POST
@login_required
def chatgroup_leave(request, pk):
    chatgroup = get_object_or_404(ChatGroup, pk=pk)
    if request.user == chatgroup.owner:
        messages.error(request, "please make someone else owner before leaving")
        return redirect("chat:chatgroup_detail", pk=pk)
    chatgroup.chat.members.remove(request.user)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "global",
        {
            "type": "remove_chat",
            "chat_pk": chatgroup.chat.pk,
            "user_pk": request.user.pk,
        },
    )
    return redirect("chat:chat")


@require_POST
@login_required
def chatgroup_makeowner(request, chatgroup_pk, user_pk):
    chatgroup = get_object_or_404(ChatGroup, pk=chatgroup_pk)
    user = get_object_or_404(User, pk=user_pk)
    if request.user != chatgroup.owner:
        raise PermissionDenied()
    chatgroup.owner = user
    chatgroup.save()
    messages.success(request, "owner changed")
    return redirect("chat:chatgroup_detail", pk=chatgroup_pk)


@require_POST
@login_required
def chatgroup_remove_member(request, chatgroup_pk, user_pk):
    chatgroup = get_object_or_404(ChatGroup, pk=chatgroup_pk)
    user = get_object_or_404(User, pk=user_pk)
    if request.user != chatgroup.owner or user == chatgroup.owner:
        raise PermissionDenied()
    chatgroup.chat.members.remove(user)
    messages.success(request, f"removed {user}")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "global",
        {
            "type": "remove_chat",
            "chat_pk": chatgroup.chat.pk,
            "user_pk": user.pk,
        },
    )
    return redirect("chat:chatgroup_detail", pk=chatgroup_pk)


@login_required
def invite_list(request, chatgroup_pk):
    chatgroup = get_object_or_404(ChatGroup, pk=chatgroup_pk)
    if request.user != chatgroup.owner:
        raise PermissionDenied()
    return render(request, "chat/invite_list.html", {"chatgroup": chatgroup})


@login_required
def invite_detail(request, invite_pk):
    invite = get_object_or_404(ChatGroupInvite, pk=invite_pk)
    if request.method == "POST":
        if not invite.chatgroup.chat.is_member(request.user):
            invite.chatgroup.chat.members.add(request.user)
            invite.uses = F("uses") + 1
            invite.save()
        return redirect("chat:chat")
    return render(request, "chat/invite_detail.html", {"invite": invite})


@require_POST
@login_required
def invite_create(request, chatgroup_pk):
    chatgroup = get_object_or_404(ChatGroup, pk=chatgroup_pk)
    if request.user != chatgroup.owner:
        raise PermissionDenied()
    invite = ChatGroupInvite.objects.create(inviter=request.user, chatgroup=chatgroup)
    messages.success(request, "invite created")
    return redirect("chat:invite_list", chatgroup_pk=chatgroup_pk)


@require_POST
@login_required
def invite_delete(request, invite_pk):
    invite = get_object_or_404(ChatGroupInvite, pk=invite_pk)
    if request.user != invite.chatgroup.owner:
        raise PermissionDenied()
    chatgroup_pk = invite.chatgroup.pk
    invite.delete()
    messages.success(request, "invite deleted")
    return redirect("chat:invite_list", chatgroup_pk=chatgroup_pk)
