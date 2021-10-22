from django import forms
from .models import ChatGroup


class ChatGroupCreateForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = ChatGroup
        fields = ("image", "name", "description")


class ChatGroupUpdateForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ("image", "name", "description")
