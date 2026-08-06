from django import template

register = template.Library()


@register.filter
def currency(value):
    try:
        amount = float(value)
    except (TypeError, ValueError):
        amount = 0.0
    if amount.is_integer():
        return format(int(amount), ",d")
    return format(amount, ",.2f")
