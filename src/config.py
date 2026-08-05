import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

HF_TOKEN = os.getenv("HF_TOKEN", "")

# Requirement 4: Model name must be declared explicitly in source code, not read from .env
HF_MODEL_ID = "Qwen/Qwen3.5-9B"
