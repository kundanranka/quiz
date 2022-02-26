from django import template
from ..models import *
register = template.Library()

@register.filter(name='is_selected')
def is_selected(value, arg):
    qs = Answers.objects.filter(user__email=arg,option__id=value.id)
    return qs.count()