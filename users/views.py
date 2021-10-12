from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from friendship.models import Friend
from .forms import UserUpdateForm

User = get_user_model()


@login_required
def profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")

            return redirect("users:profile")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, "account/profile.html", {"form": form})


@login_required
def user_list(request):
    search = request.GET.get("search")
    users = None
    if search:
        users = User.objects.filter(username__icontains=search)
    return render(request, "account/user_list.html", {"users": users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    is_friend = Friend.objects.are_friends(request.user, user)
    context = {"user": user, "is_friend": is_friend}
    return render(request, "account/user_detail.html", context)
