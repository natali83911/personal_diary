from django import template

from diary_app.utils import get_mood_style, get_tag_color

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


@register.filter
def mood_emoji(mood):
    """Возвращает emoji для настроения."""
    return get_mood_style(mood)["emoji"]


@register.filter
def mood_color(mood):
    """Возвращает цвет для настроения."""
    return get_mood_style(mood)["color"]
