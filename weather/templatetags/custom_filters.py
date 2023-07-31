from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()


@register.filter
def date_format(value):
    sep = "-"
    return " ".join([x for x in value.split(sep)][::-1])


@register.filter
def path_without_pages(value):
        return value.partition('&page')[0]