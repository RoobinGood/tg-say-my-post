import pytest

from src.preprocessing.programmatic import (
    transliterate_abbreviations,
    transliterate_numbers,
    transliterate_symbols,
    transliterate_latin_letters,
)


def test_transliterate_numbers():
    assert "тысяча" in transliterate_numbers("1500")
    assert "целых" in transliterate_numbers("2.5")
    assert "пятнадцать" in transliterate_numbers("-15")


def test_transliterate_abbreviations_known():
    result = transliterate_abbreviations("проверь API")
    assert "эй пи ай" in result.lower()
    
    result = transliterate_abbreviations("URL для HTTP")
    assert "ю ар эл" in result.lower()
    assert "эйч ти ти пи" in result.lower()


def test_transliterate_abbreviations_unknown():
    result = transliterate_abbreviations("XYZ")
    assert "кс" in result.lower() and "й" in result.lower() and "з" in result.lower()
    
    result = transliterate_abbreviations("ABC123")
    assert "а" in result.lower() and "б" in result.lower() and "к" in result.lower()


def test_transliterate_symbols():
    result = transliterate_symbols("50%")
    assert "процент" in result
    
    result = transliterate_symbols("$100")
    assert "доллар" in result


def test_transliterate_latin_letters():
    result = transliterate_latin_letters("hello")
    assert "х" in result.lower() and "е" in result.lower() and "л" in result.lower() and "о" in result.lower()
    
    result = transliterate_latin_letters("Hello World")
    assert "х" in result.lower() and "в" in result.lower()


def test_transliterate_abbreviations_integration():
    result = transliterate_abbreviations("API стоит $100")
    assert "эй пи ай" in result.lower()
    assert "$" in result
