from django import template
from apps.utils import jalali

register = template.Library()


def isalnumdate(c):
    """
    Gets a character and returns true if char is alfanum or - or /
    """
    return c.isalnum() or c in ['-', '/']


@register.filter(name='jalali')
def georgian_to_jalali(value):
    if isinstance(value, str):
        value = ''.join(c for c in value if isalnumdate(c) or c == ' ')
        value = list(value.split())
        for part in value:
            if ':' not in part:
                value = part
                break
    return jalali.Gregorian(value).persian_string()
