from django import template

register = template.Library()


@register.filter
def get_name(chat, user):
    return chat.get_name(user)


@register.filter
def get_image_url(chat, user):
    return chat.get_image(user).url


@register.filter
def get_last_message_preview(chat, user):
    return chat.get_last_message_preview(user)


@register.filter
def get_unread_messages_count(chat, user):
    return chat.get_unread_messages_count(user)
