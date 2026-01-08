import re

_EMOJI_RE = re.compile(
    "["
    "\U0000200D"  # zero width joiner
    "\U000020E3"  # combining keycap
    "\U00002100-\U000021FF"  # letterlike symbols, arrows subset
    "\U00002300-\U000023FF"  # misc technical, clocks
    "\U000025A0-\U000025FF"  # geometric shapes
    "\U00002600-\U000026FF"  # misc symbols, dingbats subset
    "\U00002700-\U000027BF"  # dingbats
    "\U0001F000-\U0001F02F"  # mahjong tiles
    "\U0001F030-\U0001F09F"  # domino tiles
    "\U0001F0A0-\U0001F0FF"  # playing cards
    "\U0001F100-\U0001F1FF"  # enclosed alphanumerics, flags subset
    "\U0001F200-\U0001F2FF"  # enclosed ideographic supplement
    "\U0001F300-\U0001F5FF"  # misc symbols and pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport and map
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # geometric extended
    "\U0001F800-\U0001F8FF"  # supplemental arrows-c
    "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
    "\U0001FA00-\U0001FAFF"  # symbols and pictographs extended-a
    "\U0001FB00-\U0001FBFF"  # symbols for legacy computing
    "\uFE0F"  # variation selector-16
    "]"
)

_URL_RE = re.compile(r"https?://[^\s]+")


def remove_emojis(text: str) -> str:
    """Remove all emoji characters from text."""
    return _EMOJI_RE.sub("", text)


def replace_leading_emoji_with_dash(line: str) -> str:
    """Replace leading emoji with dash."""
    match = _EMOJI_RE.match(line)
    if not match:
        return line
    return f"-{line[match.end():]}"


def remove_urls(text: str) -> str:
    """Remove URLs and clean up extra whitespace."""
    text = _URL_RE.sub("", text)
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines)


def capitalize_paragraphs(lines: list[str]) -> list[str]:
    """Capitalize first letter of each paragraph."""
    result: list[str] = []
    for line in lines:
        if line.strip():
            line = line.strip()
            if line:
                line = line[0].upper() + line[1:] if len(line) > 1 else line.upper()
        result.append(line)
    return result


def ensure_paragraph_periods(lines: list[str]) -> list[str]:
    """Add period at the end of each paragraph if missing."""
    result: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            last_idx = None
            for idx in range(len(paragraph) - 1, -1, -1):
                if paragraph[idx].strip():
                    last_idx = idx
                    break
            if last_idx is not None:
                line = paragraph[last_idx].rstrip()
                if line and line[-1] not in ".!?…":
                    line = f"{line}."
                paragraph[last_idx] = line
            result.extend(paragraph)
            paragraph = []

    for line in lines:
        if line.strip() == "":
            flush_paragraph()
            result.append(line)
        else:
            paragraph.append(line)

    flush_paragraph()
    return result


def enhance_paragraph_pauses(text: str) -> str:
    """Enhance pauses between paragraphs by replacing double newlines with pause markers.
    
    Many TTS systems don't properly handle paragraph breaks. This function replaces
    double newlines with multiple periods and spaces, which many TTS systems
    interpret as longer pauses than single newlines.
    """
    if not text:
        return text
    
    paragraphs = [p.strip() for p in text.split("\n\n")]
    paragraphs = [p for p in paragraphs if p]
    
    if len(paragraphs) <= 1:
        return text
    
    result_parts = []
    for i, para in enumerate(paragraphs):
        result_parts.append(para)
        if i < len(paragraphs) - 1:
            result_parts.append("... ")
    
    return " ".join(result_parts)

