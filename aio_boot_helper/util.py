from pathlib import Path
from pyunpack import Archive
import tqdm
import shutil
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

def copyfiles(files_dir, dst_dir):
    pbar = tqdm.tqdm(total=calculate_size(files_dir), unit='B', unit_scale=True)
    for file in [f for f in files_dir.glob('**/*') if f.is_file()]:
        Path.mkdir((Path(dst_dir) / file.relative_to(files_dir)).parent, parents=True, exist_ok=True)
        shutil.copyfile(file, Path(dst_dir) / file.relative_to(files_dir))
        pbar.update(file.stat().st_size)
    pbar.close()
