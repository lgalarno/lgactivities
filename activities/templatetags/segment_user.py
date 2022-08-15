from django import template

register = template.Library()


@register.simple_tag
def get_number_efforts(obj, user):
    return obj.get_number_efforts(user)


@register.simple_tag
def get_last_effort(obj, user):
    return obj.get_last_effort(user)
