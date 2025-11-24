from datetime import date

from diary_app.models import Affirmation

MOOD_STYLES = {
    "радость": {"emoji": "😄", "color": "#c3e6cb"},
    "грусть": {"emoji": "😢", "color": "#f5c6cb"},
    "спокойствие": {"emoji": "😌", "color": "#bee5eb"},
    "раздражение": {"emoji": "😠", "color": "#ffeeba"},
    "энергия": {"emoji": "⚡", "color": "#ffeeba"},
    "": {"emoji": "🙂", "color": "#e2e3e5"},
}


def get_mood_style(mood):
    return MOOD_STYLES.get(mood, MOOD_STYLES[""])


TAG_COLORS = [
    "#6f42c1",
    "#e83e8c",
    "#fd7e14",
    "#20c997",
    "#17a2b8",
    "#ffc107",
    "#007bff",
    "#28a745",
    "#dc3545",
]


def get_tag_color(idx):
    # Простой способ: назначать цвет тегу по индексу (циклично)
    return TAG_COLORS[idx % len(TAG_COLORS)]


def get_daily_affirmation():
    """Вернуть аффирмацию дня для всех пользователей (по номеру дня в году)"""
    affirmations = Affirmation.objects.filter(is_active=True).order_by("id")
    if affirmations.exists():
        day_number = date.today().timetuple().tm_yday
        return affirmations[(day_number - 1) % affirmations.count()]
    return None
