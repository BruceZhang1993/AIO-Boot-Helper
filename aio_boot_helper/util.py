from pathlib import Path
from pyunpack import Archive
from . import CHUNK_SIZE

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def decompress_file(filename):
    target_dir = filename.parent / filename.stem
    Path.mkdir(target_dir, exist_ok=True)
    Archive(filename).extractall(target_dir)

def calculate_size(path):
    return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file() )
