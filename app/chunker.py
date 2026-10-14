import re


def chunk_text(text, chunk_size=800, overlap=120):
    """Split text into readable chunks while preserving sentence boundaries."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    text = text.strip()

    if not text:
        return []

    # Split text into paragraphs using blank lines.
    paragraphs = re.split(r"\n\s*\n+", text)

    # Collect non-empty sentences.
    sentences = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        parts = re.split(r"(?<=[.!?])\s+", paragraph)
        sentences.extend(part.strip() for part in parts if part.strip())

    chunks = []
    current_sentences = []
    current_length = 0

    for sentence in sentences:
        # Handle sentences longer than the chunk size.
        if len(sentence) > chunk_size:
            if current_sentences:
                chunks.append(" ".join(current_sentences))
                current_sentences = []
                current_length = 0

            step = chunk_size - overlap

            for start in range(0, len(sentence), step):
                piece = sentence[start : start + chunk_size].strip()
                if piece:
                    chunks.append(piece)

            continue

        extra_length = len(sentence) + (1 if current_sentences else 0)

        if current_length + extra_length <= chunk_size:
            current_sentences.append(sentence)
            current_length += extra_length
            continue

        # Save the current chunk.
        chunks.append(" ".join(current_sentences))

        # Keep complete trailing sentences where possible.
        overlap_sentences = []
        overlap_length = 0

        for previous in reversed(current_sentences):
            extra = len(previous) + (1 if overlap_sentences else 0)

            if overlap_length + extra > overlap:
                break

            overlap_sentences.insert(0, previous)
            overlap_length += extra

        current_sentences = overlap_sentences
        current_length = overlap_length

        # Add the next sentence if it fits.
        extra_length = len(sentence) + (1 if current_sentences else 0)

        if current_length + extra_length <= chunk_size:
            current_sentences.append(sentence)
            current_length += extra_length
        else:
            current_sentences = [sentence]
            current_length = len(sentence)

    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks
