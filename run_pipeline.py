import json
from pathlib import Path

from config import DEFAULT_INPUT_FILE, DEFAULT_OUTPUT_FILE, OUTPUT_DIR
from ingest import load_transcript
from chunker import chunk_transcript


def infer_transcript_id(path: Path) -> str:
    return path.stem


def main() -> None:
    input_path = Path(DEFAULT_INPUT_FILE)
    output_path = Path(DEFAULT_OUTPUT_FILE)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    units = load_transcript(input_path)
    transcript_id = infer_transcript_id(input_path)

    chunks = chunk_transcript(units, transcript_id)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Loaded {len(units)} units")
    print(f"Created {len(chunks)} chunks")
    print(f"Saved to: {output_path}")

    if chunks:
        print("\nFirst chunk preview:\n")
        print(json.dumps(chunks[0], indent=2, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()