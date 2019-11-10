from pathlib import Path
from pyunpack import Archive

def decompress_file(filename):
    target_dir = filename.parent / filename.stem
    Path.mkdir(target_dir, exist_ok=True)
    Archive(filename).extractall(target_dir)
