import os
import argparse
from pathlib import Path

CACHE_DIR = Path.home() / '.cache/aio-boot-helper'
CACHE_LATEST_RELEASE = CACHE_DIR / 'latest.json'
DOWN_FILENAME = 'aio_latest.7z'
CHUNK_SIZE = 16 * 1024
COMMANDS = ['help', 'prepare', 'deploy', 'auto-deploy']

def ensure_dirs():
    """
    """
    if not Path.exists(CACHE_DIR):
        Path.mkdir(CACHE_DIR, parents=True, exist_ok=True)

def init_args():
    parser = argparse.ArgumentParser(description='AIO-Boot Helper')
    parser.add_argument('command', choices=COMMANDS, help='Command to use')
    parser.add_argument('device', nargs='?', default=None, help='Device to deploy')
    parser.add_argument('--refresh', '-r', action='store_true', default=False, help='Refresh latest release (prepare)')
    parser.add_argument('--overwrite', '-o', action='store_true', default=False, help='Force download file (prepare)')
    parser.add_argument('--yes', '-y', action='store_true', default=False, help='Disable interactive operations [DANGEROUS] (deploy)')
    return parser.parse_args(), parser
