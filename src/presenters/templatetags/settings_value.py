from django.conf import settings
from django import template

register = template.Library()

# setting value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")
