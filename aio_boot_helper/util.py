from pathlib import Path
from pyunpack import Archive
import tqdm
import shutil
from . import CHUNK_SIZE

class bcolors:
    """Color codes for terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def decompress_file(filename):
    """Decompress file to directory with same basename

    :param filename: File path to decompress
    :type filename: Path
    """
    target_dir = filename.parent / filename.stem
    Path.mkdir(target_dir, exist_ok=True)
    Archive(filename).extractall(target_dir)

def calculate_size(path):
    """Calculate size of all files in a directory recursively

    :param path: File path to calculate
    :type path: Path
    :return: Total size of files in bytes
    :rtype: int
    """
    return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file() )

def copyfiles(files_dir, dst_dir):
    """Copy files from files_dir to dst_dir

    :param files_dir: Directory/file to copy from
    :type files_dir: Path
    :param dst_dir: Directory/file to copy to
    :type dst_dir: Path
    """
    pbar = tqdm.tqdm(total=calculate_size(files_dir), unit='B', unit_scale=True)
    for file in [f for f in files_dir.glob('**/*') if f.is_file()]:
        Path.mkdir((Path(dst_dir) / file.relative_to(files_dir)).parent, parents=True, exist_ok=True)
        shutil.copyfile(file, Path(dst_dir) / file.relative_to(files_dir))
        pbar.update(file.stat().st_size)
    pbar.close()
