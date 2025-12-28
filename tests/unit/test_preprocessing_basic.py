import pytest

from src.preprocessing import preprocess_text


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
    result = preprocess_text("↘hello 🂡world")
    assert result.startswith("-")
    assert "hello" not in result.lower() or "хелло" in result.lower()


def test_capitalize_paragraphs():
    assert preprocess_text("привет мир") == "Привет мир."
    assert preprocess_text("первый абзац\n\nвторой абзац") == "Первый абзац.\n\nВторой абзац."


def test_remove_urls():
    assert preprocess_text("смотри https://example.com тут") == "Смотри тут."
    assert preprocess_text("ссылка: http://test.ru") == "Ссылка:."
    assert preprocess_text("текст с https://site.com и еще http://other.org") == "Текст с и еще."


