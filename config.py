from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

DEFAULT_INPUT_FILE = DATA_DIR / "dean_rag_chunks.json"
DEFAULT_OUTPUT_FILE = OUTPUT_DIR / "normalized_chunks.json"

TARGET_WORDS = 350
MIN_WORDS = 120
MAX_WORDS = 500

MERGE_SMALL_NEIGHBORING_CHUNKS = True