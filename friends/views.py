from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from friendship.models import Friend, FriendshipRequest

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
