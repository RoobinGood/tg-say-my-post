const leadingEmojiRegex = /^(\s*)\p{Extended_Pictographic}/u;
const emojiRegex = /\p{Extended_Pictographic}/gu;
const emojiExtrasRegex = /[\uFE0E\uFE0F\u200D]|\p{Emoji_Modifier}/gu;

export function preprocessText(input: string): string {
  let output = input;

  if (leadingEmojiRegex.test(output)) {
    output = output.replace(leadingEmojiRegex, "$1-");
  }

  output = output.replace(emojiRegex, "").replace(emojiExtrasRegex, "");
  output = capitalizeLeadingLowercase(output);
  output = ensureTrailingDot(output);

  return output;
}

function capitalizeLeadingLowercase(value: string): string {
  return value.replace(/^(\s*)(\p{Ll})/u, (_, whitespace: string, letter: string) => {
    return `${whitespace}${letter.toUpperCase()}`;
  });
}

function ensureTrailingDot(value: string): string {
  const trailingMatch = value.match(/\s*$/);
  const trailingWhitespace = trailingMatch ? trailingMatch[0] : "";
  const core = value.slice(0, value.length - trailingWhitespace.length);

  if (core.length === 0) {
    return value;
  }

  const lastChar = core.at(-1);
  if (!lastChar) {
    return value;
  }

  if ((/\p{L}|\p{N}/u).test(lastChar) && lastChar !== ".") {
    return `${core}.${trailingWhitespace}`;
  }

  return value;
}
