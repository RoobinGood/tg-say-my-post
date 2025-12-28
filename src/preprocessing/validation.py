import re

_VALID_CHARS_REGEX = re.compile(
    r'^[а-яА-ЯёЁіІїЇєЄґҐ'
    r'\s'
    r'\d'
    r'\.,!?;:\-—–'
    r'""\'\'«»'
    r'()\[\]'
    r'\+'
    r'\n]+$'
)


def validate_response(text: str) -> bool:
    """Validate that response contains only allowed characters for speech synthesis."""
    return bool(_VALID_CHARS_REGEX.match(text))

