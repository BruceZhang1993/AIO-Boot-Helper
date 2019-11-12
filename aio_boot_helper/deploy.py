import asyncio
import os
from pathlib import Path
import tqdm
import shutil
from .util import calculate_size, bcolors
from . import CHUNK_SIZE

async def run_command(*args, allow_fail=False):
    print(bcolors.BOLD + 'Running:' + bcolors.ENDC + ' {}'.format(' '.join(args)))
    process = await asyncio.create_subprocess_exec(
        *args,
        stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if not allow_fail and process.returncode != 0:
        raise Exception(stderr.decode().strip())
    return stdout.decode().strip(), stderr.decode().strip(), process.returncode

async def check_exists(command):
    print(bcolors.BOLD + 'Running:' + bcolors.ENDC + ' which {}'.format(command))
    process = await asyncio.create_subprocess_exec(
        'which', command,
        stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    await process.communicate()
    return process.returncode == 0

async def deploy_aio(device, noask=False):
    commands = {
        'grub-bios-setup': 'grub2',
        'udisksctl': 'udisks2'
    }
    for k in commands:
        if await check_exists(k):
            print('Found: {}'.format(k))
        else:
            raise Exception('Please install {}.'.format(commands.get(k)))
    if not noask:
        print(bcolors.WARNING + bcolors.BOLD + '[DANGEROUS] This command will wrap out {}, please BACKUP your data first. \nInput `YES` and press [ENTER] to continue, [Ctrl-C] to abort: '.format(device), end=bcolors.ENDC)
        if input() != "YES":
            raise Exception('User aborted.')
    print('Unmounting device {} ...'.format(device))
    await run_command('udisksctl', 'unmount', '-f', '-b', device, allow_fail=True)
    await run_command('sudo', 'umount', device, allow_fail=True)
    await run_command('sudo', 'mkfs.vfat', '-n', 'AIOBOOT', '-F', '32', device)
    aio_grub_dir = Path.cwd() / 'aio/aio_latest/AIO/grub/i386-pc'
    out, _, __ = await run_command('sudo', 'grub-bios-setup', '-d', aio_grub_dir, device)
    print(out)
    print('Mounting device {} ...'.format(device))
    await run_command('udisksctl', 'mount', '-b', device, allow_fail=True)
    print('Copying AIO files...')
    files_dir = Path.cwd() / 'aio/aio_latest'
    pbar = tqdm.tqdm(total=calculate_size(files_dir), unit='B', unit_scale=True)
    for file in [f for f in files_dir.glob('**/*') if f.is_file()]:
        Path.mkdir((Path('/home/bruce/test') / file.relative_to(files_dir)).parent, parents=True, exist_ok=True)
        shutil.copyfile(file, Path('/home/bruce/test') / file.relative_to(files_dir))
        pbar.update(file.stat().st_size)
    pbar.close()
    print('Unmounting device {} ...'.format(device))
    await run_command('udisksctl', 'unmount', '-f', '-b', device, allow_fail=True)
    print(bcolors.OKGREEN + bcolors.BOLD + 'All done. Have fun!' + bcolors.ENDC)
