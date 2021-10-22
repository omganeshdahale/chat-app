from django.urls import path
from .views import *

app_name = "chat"

urlpatterns = [
    path("", chat, name="chat"),
    path("chatgroup/create/", chatgroup_create, name="chatgroup_create"),
    path("chatgroup/<int:pk>/", chatgroup_detail, name="chatgroup_detail"),
    path("chatgroup/<int:pk>/edit/", chatgroup_edit, name="chatgroup_edit"),
    path("chatgroup/<int:pk>/delete/", chatgroup_delete, name="chatgroup_delete"),
    path("chatgroup/<int:pk>/leave/", chatgroup_leave, name="chatgroup_leave"),
    path(
        "chatgroup/<int:chatgroup_pk>/makeowner/<int:user_pk>/",
        chatgroup_makeowner,
        name="chatgroup_makeowner",
    ),
    path(
        "chatgroup/<int:chatgroup_pk>/remove/<int:user_pk>/",
        chatgroup_remove_member,
        name="chatgroup_remove_member",
    ),
    path("chatgroup/<int:chatgroup_pk>/invites/", invite_list, name="invite_list"),
    path(
        "chatgroup/<int:chatgroup_pk>/invites/create/",
        invite_create,
        name="invite_create",
    ),
    path("chatgroup/invite/<uuid:invite_pk>/", invite_detail, name="invite_detail"),
    path(
        "chatgroup/invite/<uuid:invite_pk>/delete/", invite_delete, name="invite_delete"
    ),
]
