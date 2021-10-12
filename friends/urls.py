from django.urls import path
from friendship.views import (
    friendship_reject,
)
from .views import *

urlpatterns = [
    path(
        "friends/",
        view=friend_list,
        name="friend_list",
    ),
    path(
        "friend/add/<slug:to_username>/",
        view=friendship_add_friend,
        name="friendship_add_friend",
    ),
    path(
        "friend/requests/",
        view=friendship_request_list,
        name="friendship_request_list",
    ),
    path(
        "friend/requests/rejected/",
        view=friendship_request_list_rejected,
        name="friendship_requests_rejected",
    ),
    path(
        "friend/request/<int:friendship_request_id>/",
        view=friendship_requests_detail,
        name="friendship_requests_detail",
    ),
    path(
        "friend/accept/<int:friendship_request_id>/",
        view=friendship_accept,
        name="friendship_accept",
    ),
    path(
        "friend/reject/<int:friendship_request_id>/",
        view=friendship_reject,
        name="friendship_reject",
    ),
    path(
        "friend/remove/<int:pk>/",
        view=remove_friend,
        name="remove_friend",
    ),
]
