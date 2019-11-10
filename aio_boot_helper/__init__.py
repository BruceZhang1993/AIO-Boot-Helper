import os
from pathlib import Path

CACHE_DIR = Path.home() / '.cache/aio-boot-helper'
CACHE_LATEST_RELEASE = CACHE_DIR / 'latest.json'
DOWN_FILENAME = 'aio_latest.7z'
CHUNK_SIZE = 1024

def ensure_dirs():
    if not Path.exists(CACHE_DIR):
        Path.mkdir(CACHE_DIR, parents=True, exist_ok=True)

ensure_dirs()
