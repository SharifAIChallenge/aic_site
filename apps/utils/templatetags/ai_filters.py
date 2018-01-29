from django import template
from apps.utils import jalali

register = template.Library()


@register.filter(name='jalali')
def georgian_to_jalali(value):
    if isinstance(value, str):
        value = list(value.split())[0]
    # return value
    return jalali.Gregorian(value).persian_string()
