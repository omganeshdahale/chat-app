from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from friendship.exceptions import AlreadyExistsError
from friendship.models import Block, Friend, FriendshipRequest

User = get_user_model()


@login_required
def friendship_request_list(
    request, template_name="friendship/friend/requests_list.html"
):
    friendship_requests = Friend.objects.unrejected_requests(request.user)

    return render(request, template_name, {"requests": friendship_requests})


@login_required
def friendship_request_list_rejected(
    request, template_name="friendship/friend/rejected_requests_list.html"
):
    """View rejected friendship requests"""
    friendship_requests = Friend.objects.rejected_requests(request.user)

    return render(request, template_name, {"requests": friendship_requests})


@login_required
def friend_list(request, template_name="friendship/friend/friend_list.html"):
    friends = Friend.objects.friends(request.user)
    return render(
        request,
        template_name,
        {
            "friends": friends,
        },
    )


@login_required
def friendship_add_friend(
    request, to_username, template_name="friendship/friend/add.html"
):
    """Create a FriendshipRequest"""
    ctx = {"to_username": to_username}

    if request.method == "POST":
        to_user = User.objects.get(username=to_username)
        from_user = request.user
        try:
            Friend.objects.add_friend(from_user, to_user)
        except AlreadyExistsError as e:
            ctx["errors"] = ["%s" % e]
        else:
            messages.success(request, "Friend request sent")
            return redirect("friendship_request_list")

    return render(request, template_name, ctx)


@login_required
def friendship_requests_detail(
    request, friendship_request_id, template_name="friendship/friend/request.html"
):
    """View a particular friendship request"""
    f_request = get_object_or_404(FriendshipRequest, id=friendship_request_id)
    if not f_request.viewed and request.user == f_request.to_user:
        f_request.mark_viewed()

    return render(request, template_name, {"friendship_request": f_request})


@login_required
def friendship_accept(request, friendship_request_id):
    """Accept a friendship request"""
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.friendship_requests_received, id=friendship_request_id
        )
        f_request.accept()
        return redirect("friend_list")

    return redirect(
        "friendship_requests_detail", friendship_request_id=friendship_request_id
    )


@require_POST
@login_required
def remove_friend(request, pk):
    friend = get_object_or_404(User, pk=pk)
    Friend.objects.remove_friend(request.user, friend)
    messages.success(request, f"Removed friend {friend}")

    return redirect("users:user_detail", username=friend.username)


@login_required
def block_list(request):
    blocking = Block.objects.blocking(request.user)
    return render(request, "friendship/block/block_list.html", {"blocking": blocking})


@login_required
def block_add(request, blocked_username, template_name="friendship/block/add.html"):
    """Create a following relationship"""
    ctx = {"blocked_username": blocked_username}

    if request.method == "POST":
        blocked = User.objects.get(username=blocked_username)
        blocker = request.user
        try:
            Block.objects.add_block(blocker, blocked)
        except AlreadyExistsError as e:
            ctx["errors"] = ["%s" % e]
        else:
            messages.success(request, f"blocked {blocked}")
            return redirect("users:user_detail", username=blocked_username)

    return render(request, template_name, ctx)


@login_required
def block_remove(
    request, blocked_username, template_name="friendship/block/remove.html"
):
    """Remove a following relationship"""
    if request.method == "POST":
        blocked = User.objects.get(username=blocked_username)
        blocker = request.user
        Block.objects.remove_block(blocker, blocked)
        messages.success(request, f"unblocked {blocked}")
        return redirect("users:user_detail", username=blocked_username)

    return render(request, template_name, {"blocked_username": blocked_username})
