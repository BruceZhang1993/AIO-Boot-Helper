from pathlib import Path
from pyunpack import Archive
from . import CHUNK_SIZE

def decompress_file(filename):
    target_dir = filename.parent / filename.stem
    Path.mkdir(target_dir, exist_ok=True)
    Archive(filename).extractall(target_dir)

def calculate_size(path):
    return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file() )
