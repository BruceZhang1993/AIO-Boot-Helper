import asyncio
import os
from pathlib import Path
import tqdm
import shutil
from .util import calculate_size
from . import CHUNK_SIZE

async def run_command(*args, allow_fail=False):
    print('Running: {}'.format(' '.join(args)))
    process = await asyncio.create_subprocess_exec(
        *args,
        stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if not allow_fail and process.returncode != 0:
        raise Exception(stderr.decode().strip())
    return stdout.decode().strip(), stderr.decode().strip(), process.returncode

async def check_exists(command):
    print('Running: which {}'.format(command))
    process = await asyncio.create_subprocess_exec(
        'which', command,
        stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    await process.communicate()
    return process.returncode == 0

async def deploy_aio(device, noask=False):
    copied_bytes = 0
    def _copied(_):
        pbar.update(CHUNK_SIZE)
    command = 'grub-bios-setup'
    if await check_exists(command):
        print('Found: {}'.format(command))
    else:
        raise Exception('Please install grub2.')
    if not noask:
        print('[DANGEROUS] This command will wrap out {}, please backup your data first. Input `YES` and press [ENTER] to continue, [Ctrl-C] to abort: '.format(device), end='')
        if input() != "YES":
            raise Exception('User aborted.')
    await run_command('sudo', 'umount', device, allow_fail=True)
    await run_command('sudo', 'mkfs.vfat', '-n', 'AIOBOOT', device)
    aio_grub_dir = Path.cwd() / 'aio/aio_latest/AIO/grub/i386-pc'
    out, _, __ = await run_command('sudo', 'grub-bios-setup', '-d', aio_grub_dir, device)
    print(out)
    print('Copying AIO files...')
    files_dir = Path.cwd() / 'aio/aio_latest'
    pbar = tqdm.tqdm(total=calculate_size(files_dir), unit='B', unit_scale=True)
    for file in [f for f in files_dir.glob('**/*') if f.is_file()]:
        Path.mkdir((Path('/home/bruce/test') / file.relative_to(files_dir)).parent, parents=True, exist_ok=True)
        shutil.copyfile(file, Path('/home/bruce/test') / file.relative_to(files_dir))
        pbar.update(file.stat().st_size)
    pbar.close()
    print('Copied.')
