from django import template

register = template.Library()


@register.filter
def get_name(chat, user):
    return chat.get_name(user)


@register.filter
def get_image_url(chat, user):
    return chat.get_image(user).url
