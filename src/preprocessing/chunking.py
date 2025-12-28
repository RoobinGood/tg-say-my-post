from dataclasses import dataclass

import tiktoken


@dataclass
class TextChunk:
    text: str
    start_index: int
    end_index: int


def split_into_chunks(text: str, min_chunk_size: int, max_tokens: int) -> list[TextChunk]:
    """Split text into chunks suitable for LLM processing."""
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    paragraphs = text.split("\n\n")
    chunks: list[TextChunk] = []
    current_chunk = ""
    start_idx = 0

    for para in paragraphs:
        if not para.strip():
            continue

        para_with_newline = para + "\n\n"
        test_chunk = current_chunk + para_with_newline if current_chunk else para_with_newline

        tokens = len(encoding.encode(test_chunk))

        if tokens > max_tokens and current_chunk:
            chunks.append(TextChunk(
                text=current_chunk.strip(),
                start_index=start_idx,
                end_index=start_idx + len(current_chunk),
            ))
            start_idx += len(current_chunk)
            current_chunk = para_with_newline
        elif len(test_chunk) >= min_chunk_size and current_chunk:
            chunks.append(TextChunk(
                text=current_chunk.strip(),
                start_index=start_idx,
                end_index=start_idx + len(current_chunk),
            ))
            start_idx += len(current_chunk)
            current_chunk = para_with_newline
        else:
            current_chunk = test_chunk

    if current_chunk.strip():
        chunks.append(TextChunk(
            text=current_chunk.strip(),
            start_index=start_idx,
            end_index=start_idx + len(current_chunk),
        ))

    return chunks if chunks else [TextChunk(text=text, start_index=0, end_index=len(text))]

