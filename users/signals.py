from django.dispatch import receiver
import requests
from django.core import files
from io import BytesIO
from allauth.account.signals import user_signed_up


@receiver(user_signed_up)
def populate_profile(user, sociallogin=None, **kwargs):
    url = f"https://ui-avatars.com/api/?name={user.username}&size=96&bold=true&background=random"
    if sociallogin and sociallogin.account.provider == "google":
        extra_data = user.socialaccount_set.filter(provider="google")[0].extra_data
        url = extra_data["picture"]
    response = requests.get(url)
    fp = BytesIO()
    fp.write(response.content)
    user.profile_pic.save(f"{user.id}.png", files.File(fp))
    user.save()
