from django import template

register = template.Library()


@register.filter
def spaced(value):
    if value is None:
        return '0'
    num = float(value)
    is_neg = num < 0
    num = abs(num)
    int_part = int(num)
    frac = num - int_part
    int_str = str(int_part)
    result = ''
    while int_str:
        if len(int_str) <= 3:
            result = int_str + result
            int_str = ''
        else:
            result = ' ' + int_str[-3:] + result
            int_str = int_str[:-3]
    if frac >= 0.005:
        result += f'{frac:.2f}'[1:]
    return ('-' if is_neg else '') + result
