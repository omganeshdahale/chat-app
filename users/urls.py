from django.urls import path
from .views import *

app_name = "users"

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("users/", user_list, name="user_list"),
    path("user/<username>/", user_detail, name="user_detail"),
]
