import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from num2words import num2words


@dataclass
class TranslitConfig:
    abbreviations: dict[str, str]
    symbols: dict[str, str]
    units: dict[str, str]


def _load_translit_config(config_path: Optional[Path] = None) -> TranslitConfig:
    if config_path is None:
        project_root = Path(__file__).resolve().parents[2]
        config_path = project_root / "src" / "preprocessing" / "dictionaries" / "transliteration.json"

    if not config_path.exists():
        return TranslitConfig(abbreviations={}, symbols={}, units={})

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return TranslitConfig(
        abbreviations=data.get("abbreviations", {}),
        symbols=data.get("symbols", {}),
        units=data.get("units", {}),
    )


def _load_latin_letters_dict(dict_path: Optional[Path] = None) -> dict[str, str]:
    if dict_path is None:
        project_root = Path(__file__).resolve().parents[2]
        dict_path = project_root / "src" / "preprocessing" / "dictionaries" / "latin_letters.json"

    if not dict_path.exists():
        return {}

    with open(dict_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_abbreviation_letters_dict(dict_path: Optional[Path] = None) -> dict[str, str]:
    if dict_path is None:
        project_root = Path(__file__).resolve().parents[2]
        dict_path = project_root / "src" / "preprocessing" / "dictionaries" / "abbreviation_letters.json"

    if not dict_path.exists():
        return {}

    with open(dict_path, "r", encoding="utf-8") as f:
        return json.load(f)


def transliterate_numbers(text: str) -> str:
    def replace_number(match: re.Match[str]) -> str:
        num_str = match.group(0)
        try:
            if "/" in num_str:
                parts = num_str.split("/")
                if len(parts) == 2:
                    try:
                        numerator = int(parts[0])
                        denominator = int(parts[1])
                        return num2words(numerator, lang="ru") + " " + num2words(denominator, lang="ru", to="ordinal")
                    except ValueError:
                        return num_str
            elif "." in num_str:
                return num2words(float(num_str), lang="ru")
            else:
                return num2words(int(num_str), lang="ru")
        except (ValueError, OverflowError):
            return num_str

    number_pattern = r"-?\d+(?:\.\d+)?(?:/\d+)?"
    return re.sub(number_pattern, replace_number, text)


def transliterate_abbreviations(text: str, config_path: Optional[Path] = None) -> str:
    config = _load_translit_config(config_path)
    abbreviation_letters_dict = _load_abbreviation_letters_dict()

    result = text

    known_abbr_pattern = re.compile(
        r"\b(" + "|".join(re.escape(abbr) for abbr in config.abbreviations.keys()) + r")\b",
        re.IGNORECASE
    )

    def replace_known(match: re.Match[str]) -> str:
        abbr = match.group(0)
        for known_abbr, replacement in config.abbreviations.items():
            if abbr.upper() == known_abbr.upper():
                return replacement
        return abbr

    result = known_abbr_pattern.sub(replace_known, result)

    unknown_abbr_pattern = re.compile(r"\b[A-Z]{2,}(?:[0-9]+)?\b")

    def transliterate_letter_by_letter(match: re.Match[str]) -> str:
        abbr = match.group(0)
        words = []
        for char in abbr:
            if char.isalpha() and char in abbreviation_letters_dict:
                transliterated = abbreviation_letters_dict[char]
                words.append(transliterated)
            elif char.isdigit():
                words.append(char)
        return " ".join(words) if words else abbr

    result = unknown_abbr_pattern.sub(transliterate_letter_by_letter, result)

    return result


def transliterate_symbols(text: str, config_path: Optional[Path] = None) -> str:
    config = _load_translit_config(config_path)
    result = text
    for symbol, replacement in config.symbols.items():
        result = result.replace(symbol, replacement)
    return result


def transliterate_latin_letters(text: str, config_path: Optional[Path] = None) -> str:
    latin_dict = _load_latin_letters_dict(config_path)

    result = []
    for char in text:
        result.append(latin_dict.get(char, char))
    return "".join(result)
