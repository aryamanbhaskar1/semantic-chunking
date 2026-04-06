from typing import Dict, List

from config import TARGET_WORDS, MIN_WORDS, MAX_WORDS, MERGE_SMALL_NEIGHBORING_CHUNKS


def word_count(text: str) -> int:
    return len(text.split())


def build_chunk_text(units: List[Dict]) -> str:
    parts = []
    for unit in units:
        speaker = unit["speaker"]
        role = unit.get("role", "")
        text = unit["text"]

        header = speaker
        if role:
            header += f" ({role})"

        parts.append(f"{header}:\n{text}")

    return "\n\n".join(parts)


def finalize_chunk(units: List[Dict], transcript_id: str, chunk_idx: int) -> Dict:
    speakers = []
    seen_speakers = set()

    sources = []
    seen_sources = set()

    for unit in units:
        speaker = unit["speaker"]
        source = unit.get("source", "")

        if speaker not in seen_speakers:
            seen_speakers.add(speaker)
            speakers.append(speaker)

        if source and source not in seen_sources:
            seen_sources.add(source)
            sources.append(source)

    text = build_chunk_text(units)

    return {
        "chunk_id": f"{transcript_id}_chunk_{chunk_idx:03d}",
        "transcript_id": transcript_id,
        "sources": sources,
        "speakers": speakers,
        "start_timestamp_ms": units[0].get("timestamp_ms"),
        "end_timestamp_ms": units[-1].get("timestamp_ms"),
        "word_count": word_count(text),
        "text": text,
    }


def chunk_transcript(units: List[Dict], transcript_id: str) -> List[Dict]:
    """
    V1:
    - if records are already reasonable size, keep them
    - merge neighboring small records
    - don't exceed max size
    """
    chunks = []
    current_units = []
    current_words = 0
    chunk_idx = 1

    for unit in units:
        unit_words = word_count(unit["text"])

        # If current chunk is empty, start it
        if not current_units:
            current_units.append(unit)
            current_words = unit_words
            continue

        # Merge small neighboring chunks if enabled
        should_merge = (
            MERGE_SMALL_NEIGHBORING_CHUNKS
            and current_words < MIN_WORDS
            and current_words + unit_words <= MAX_WORDS
        )

        # General size-based accumulation
        should_append = (
            current_words + unit_words <= TARGET_WORDS
        )

        if should_merge or should_append:
            current_units.append(unit)
            current_words += unit_words
        else:
            chunks.append(finalize_chunk(current_units, transcript_id, chunk_idx))
            chunk_idx += 1

            current_units = [unit]
            current_words = unit_words

    if current_units:
        chunks.append(finalize_chunk(current_units, transcript_id, chunk_idx))

    return chunks