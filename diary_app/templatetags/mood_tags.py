from django import template

from diary_app.utils import get_tag_color

register = template.Library()


@register.filter
def get_item(dictionary, key):
    # Уверено возвращаем словарь или дефолт
    if isinstance(dictionary, dict):
        return dictionary.get(key) or dictionary.get("")
    return {}


@register.filter
def dict_key(d, key):
    if isinstance(d, dict):
        return d.get(key, "")
    return ""


@register.filter
def tag_color(idx):
    return get_tag_color(idx)
