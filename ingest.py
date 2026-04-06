import json
from pathlib import Path
from typing import Any, Dict, List


def clean_text(text: Any) -> str:
    if text is None:
        return ""
    return " ".join(str(text).strip().split())


def normalize_speaker(speaker: Any) -> str:
    if speaker is None:
        return "Unknown"
    speaker = str(speaker).strip()
    return speaker if speaker else "Unknown"


def normalize_rag_record(record: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """
    Normalize a dean_rag_chunks.json-style record into a standard unit.
    """
    context = clean_text(record.get("context", ""))
    content = clean_text(record.get("content", ""))

    combined_text = content
    if context:
        combined_text = f"Context: {context}\n\nResponse: {content}"

    return {
        "unit_id": idx,
        "source": clean_text(record.get("source", "")),
        "speaker": normalize_speaker(record.get("speaker")),
        "role": clean_text(record.get("role", "")),
        "timestamp_ms": record.get("timestamp_ms"),
        "text": combined_text,
    }


def normalize_text_only_record(record: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """
    Normalize simple json/jsonl records like {"text": "..."}.
    """
    return {
        "unit_id": idx,
        "source": clean_text(record.get("source", "")),
        "speaker": normalize_speaker(record.get("speaker")),
        "role": clean_text(record.get("role", "")),
        "timestamp_ms": record.get("timestamp_ms"),
        "text": clean_text(
            record.get("text")
            or record.get("content")
            or record.get("output")
            or ""
        ),
    }


def normalize_record(record: Dict[str, Any], idx: int) -> Dict[str, Any]:
    if "content" in record or "context" in record:
        return normalize_rag_record(record, idx)
    return normalize_text_only_record(record, idx)


def load_json_file(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected top-level JSON array.")

    units = []
    for idx, record in enumerate(data):
        if not isinstance(record, dict):
            continue
        unit = normalize_record(record, idx)
        if unit["text"]:
            units.append(unit)

    return units


def load_jsonl_file(path: Path) -> List[Dict[str, Any]]:
    units = []
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                continue
            unit = normalize_record(record, idx)
            if unit["text"]:
                units.append(unit)

    return units


def load_transcript(path: Path) -> List[Dict[str, Any]]:
    suffix = path.suffix.lower()

    if suffix == ".json":
        return load_json_file(path)
    if suffix == ".jsonl":
        return load_jsonl_file(path)

    raise ValueError(f"Unsupported file type: {suffix}")