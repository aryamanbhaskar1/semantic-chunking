from typing import Dict, List, Optional

from config import (
    TARGET_WORDS,
    MIN_WORDS,
    MAX_WORDS,
    OVERLAP_UNITS,
    TIMESTAMP_GAP_THRESHOLD_MS,
    SPLIT_ON_SPEAKER_CHANGE,
    INCLUDE_CONTEXT_IN_TEXT,
    MAX_CONTEXT_WORDS,
)


def word_count(text: str) -> int:
    return len(text.split())


def truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + " ..."


def format_unit_text(unit: Dict) -> str:
    speaker = unit["speaker"]
    role = unit.get("role", "")
    content = unit.get("content", "") or unit.get("text", "")
    context = unit.get("context", "")

    header = speaker
    if role:
        header += f" ({role})"

    if INCLUDE_CONTEXT_IN_TEXT and context:
        short_context = truncate_words(context, MAX_CONTEXT_WORDS)
        return f"{header}:\nContext: {short_context}\nResponse: {content}"

    return f"{header}:\n{content}"


def build_chunk_text(units: List[Dict]) -> str:
    return "\n\n".join(format_unit_text(unit) for unit in units)


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
        "unit_count": len(units),
        "contexts": [u.get("context", "") for u in units if u.get("context")],
        "text": text,
    }


def get_timestamp_gap_ms(prev_unit: Dict, next_unit: Dict) -> Optional[int]:
    prev_ts = prev_unit.get("timestamp_ms")
    next_ts = next_unit.get("timestamp_ms")

    if prev_ts is None or next_ts is None:
        return None

    try:
        return int(next_ts) - int(prev_ts)
    except (TypeError, ValueError):
        return None


def should_split(current_units: List[Dict], current_words: int, next_unit: Dict) -> bool:
    if not current_units:
        return False

    next_words = word_count(format_unit_text(next_unit))
    prev_unit = current_units[-1]

    # Hard max size
    if current_words + next_words > MAX_WORDS:
        return True

    # Timestamp gap split
    gap = get_timestamp_gap_ms(prev_unit, next_unit)
    if gap is not None and gap > TIMESTAMP_GAP_THRESHOLD_MS and current_words >= MIN_WORDS:
        return True

    # Speaker change split
    speaker_changed = next_unit["speaker"] != prev_unit["speaker"]
    if SPLIT_ON_SPEAKER_CHANGE and speaker_changed and current_words >= TARGET_WORDS:
        return True

    return False


def chunk_transcript(units: List[Dict], transcript_id: str) -> List[Dict]:
    chunks = []
    current_units: List[Dict] = []
    current_words = 0
    chunk_idx = 1

    for unit in units:
        formatted_unit = format_unit_text(unit)
        unit_words = word_count(formatted_unit)

        if current_units and should_split(current_units, current_words, unit):
            chunks.append(finalize_chunk(current_units, transcript_id, chunk_idx))
            chunk_idx += 1

            overlap = current_units[-OVERLAP_UNITS:] if OVERLAP_UNITS > 0 else []
            current_units = overlap.copy()
            current_words = sum(word_count(format_unit_text(u)) for u in current_units)

        current_units.append(unit)
        current_words += unit_words

        if current_words >= TARGET_WORDS:
            chunks.append(finalize_chunk(current_units, transcript_id, chunk_idx))
            chunk_idx += 1

            overlap = current_units[-OVERLAP_UNITS:] if OVERLAP_UNITS > 0 else []
            current_units = overlap.copy()
            current_words = sum(word_count(format_unit_text(u)) for u in current_units)

    if current_units:
        chunks.append(finalize_chunk(current_units, transcript_id, chunk_idx))

    return chunks