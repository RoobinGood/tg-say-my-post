const MAX_CHUNK_SIZE = 4000;

export function splitTextForSalute(text: string): string[] {
  if (text.length <= MAX_CHUNK_SIZE) {
    return [text];
  }

  const chunks: string[] = [];
  const paragraphs = text.split(/\n\s*\n/);
  let currentChunk = "";

  for (const paragraph of paragraphs) {
    if (paragraph.trim().length === 0) {
      continue;
    }

    const trimmedParagraph = paragraph.trim();
    const separator = currentChunk ? "\n\n" : "";

    if (trimmedParagraph.length <= MAX_CHUNK_SIZE) {
      const potentialChunk = currentChunk
        ? `${currentChunk}${separator}${trimmedParagraph}`
        : trimmedParagraph;

      if (potentialChunk.length <= MAX_CHUNK_SIZE) {
        currentChunk = potentialChunk;
      } else {
        if (currentChunk) {
          chunks.push(currentChunk);
        }
        currentChunk = trimmedParagraph;
      }
    } else {
      if (currentChunk) {
        chunks.push(currentChunk);
        currentChunk = "";
      }

      const sentences = splitIntoSentences(trimmedParagraph);
      let sentenceChunk = "";

      for (const sentence of sentences) {
        const potentialChunk = sentenceChunk
          ? `${sentenceChunk} ${sentence}`
          : sentence;

        if (potentialChunk.length <= MAX_CHUNK_SIZE) {
          sentenceChunk = potentialChunk;
        } else {
          if (sentenceChunk) {
            chunks.push(sentenceChunk.trim());
          }

          if (sentence.length > MAX_CHUNK_SIZE) {
            const forcedChunks = forceSplit(sentence, MAX_CHUNK_SIZE);
            chunks.push(...forcedChunks);
            sentenceChunk = "";
          } else {
            sentenceChunk = sentence;
          }
        }
      }

      if (sentenceChunk) {
        chunks.push(sentenceChunk.trim());
      }
    }
  }

  if (currentChunk) {
    chunks.push(currentChunk);
  }

  return chunks.length > 0 ? chunks : [text];
}

function splitIntoSentences(text: string): string[] {
  const sentenceEndings = /([.!?]+\s*)/;
  const sentences: string[] = [];
  let remaining = text;

  while (remaining.length > 0) {
    const match = remaining.match(sentenceEndings);
    if (!match) {
      if (remaining.trim()) {
        sentences.push(remaining.trim());
      }
      break;
    }

    const endIndex = match.index! + match[0].length;
    const sentence = remaining.slice(0, endIndex).trim();
    if (sentence) {
      sentences.push(sentence);
    }
    remaining = remaining.slice(endIndex);
  }

  return sentences.length > 0 ? sentences : [text];
}

function forceSplit(text: string, maxSize: number): string[] {
  const chunks: string[] = [];
  let remaining = text;

  while (remaining.length > 0) {
    if (remaining.length <= maxSize) {
      chunks.push(remaining);
      break;
    }

    const chunk = remaining.slice(0, maxSize);
    const lastSpace = chunk.lastIndexOf(" ");
    const splitPoint = lastSpace > maxSize * 0.8 ? lastSpace : maxSize;
    chunks.push(remaining.slice(0, splitPoint).trim());
    remaining = remaining.slice(splitPoint).trim();
  }

  return chunks;
}
