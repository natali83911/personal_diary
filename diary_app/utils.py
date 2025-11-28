from datetime import date


def get_mood_style(mood: str | None) -> dict:
    """
    Возвращает оформление для настроения:
    emoji + цвет. Примерная реализация — подстрой под свои значения.
    """
    mapping = {
        "радость": {"emoji": "😊", "color": "#4caf50"},
        "спокойствие": {"emoji": "😌", "color": "#2196f3"},
        "грусть": {"emoji": "😢", "color": "#9e9e9e"},
        "злость": {"emoji": "😡", "color": "#f44336"},
        "раздражение": {"emoji": "😤", "color": "#ff9800"},
        "энергия": {"emoji": "⚡", "color": "#ffeb3b"},
        "личное": {"emoji": "📝", "color": "#9c27b0"},
    }

    return mapping.get(mood or "", {"emoji": "•", "color": "#757575"})


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
    from diary_app.models import Affirmation

    """Вернуть аффирмацию дня для всех пользователей (по номеру дня в году)"""
    affirmations = Affirmation.objects.filter(is_active=True).order_by("id")
    if affirmations.exists():
        day_number = date.today().timetuple().tm_yday
        return affirmations[(day_number - 1) % affirmations.count()]
    return None
