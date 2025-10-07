import json
from pathlib import Path
from typing import List, Dict
import config

# Use centralized config
UPLOADS_DIR = config.UPLOADS_DIR

def delete_file(filename: str) -> bool:
    fp = UPLOADS_DIR / filename
    if fp.exists():
        try:
            fp.unlink()
        except Exception:
            pass
    return True
