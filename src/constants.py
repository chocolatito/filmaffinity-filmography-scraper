from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(".env")
BASE_DIR = str(Path(__file__).parents[1])
LOG_NAME = f"{Path(__file__).parents[1].parts[-1]}.log"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 1))
PROXY = os.getenv("PROXY", None)
