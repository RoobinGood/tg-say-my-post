import pytest

from src.bot.text_preprocess import preprocess_text


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Привет\n\nКак дела", "Привет.\n\nКак дела."),
        ("Уже есть знак!", "Уже есть знак!"),
    ],
)
def test_add_period_per_paragraph(text, expected):
    assert preprocess_text(text) == expected


def test_replace_leading_emoji_and_remove_all():
    assert preprocess_text("😀Привет 😀мир") == "-Привет мир."


def test_remove_only_emojis_results_empty():
    assert preprocess_text("😀😁") == "-."


def test_square_bullet_is_removed_and_dash_added():
    assert preprocess_text("▪️Пункт списка") == "-Пункт списка."


def test_arrow_and_playing_card_removed():
    assert preprocess_text("↘hello 🂡world") == "-hello world."


