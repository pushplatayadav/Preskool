from django import template

register = template.Library()


@register.filter
def index(value, key):
    """Index into a list/dict using a key (list position or dict key)."""
    if value is None:
        return None
    try:
        return value[key]
    except (KeyError, IndexError, TypeError):
        return None
