import asyncio
import os
from pathlib import Path
import tqdm
import shutil
import re
from .util import calculate_size, bcolors, copyfiles
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

async def get_mount_point(device):
    await asyncio.sleep(1)
    out, _, __ = await run_command('udisksctl', 'info', '-b', device + '1')
    line = list(filter(lambda l: l.find('MountPoints:') >= 0, out.split('\n')))
    return line[0].strip().split()[1]

async def deploy_aio(device, noask=False):
    commands = {
        'grub-bios-setup': 'grub2',
        'udisksctl': 'udisks2',
        'wipefs': 'util-linux',
        'parted': 'parted'
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
    await run_command('udisksctl', 'unmount', '-f', '-b', device + '1', allow_fail=True)
    await run_command('sudo', 'umount', device, allow_fail=True)
    await run_command('sudo', 'wipefs', '--all', device)
    await run_command('sudo', 'parted', device, 'mklabel', 'msdos')
    await run_command('sudo', 'parted', '--align=opt', device, 'mkpart', 'primary', '0%', '100%')
    await run_command('sudo', 'mkfs.vfat', '-n', 'AIOBOOT', '-F', '32', device + '1')
    print('Mounting device {} ...'.format(device))
    await asyncio.sleep(3)
    await run_command('udisksctl', 'mount', '-b', device + '1')
    mounting_point = await get_mount_point(device)
    print('Copying AIO files to {} ...'.format(mounting_point))
    files_dir = Path.cwd() / 'aio/aio_latest'
    copyfiles(files_dir, mounting_point)
    print('Copying grub files...')
    files_dir = files_dir / 'AIO/grub'
    copyfiles(files_dir, mounting_point + '/boot/grub')
    print('Installing grub2...')
    out, _, __ = await run_command('sudo', 'grub-install', '--target=i386-pc', '--root-directory=' + mounting_point, device)
    print('Unmounting device {} ...'.format(device))
    await run_command('udisksctl', 'unmount', '-f', '-b', device + '1', allow_fail=True)
    await run_command('sudo', 'sync', device, allow_fail=True)
    await run_command('sudo', 'sync', device + '1', allow_fail=True)
    print(bcolors.OKGREEN + bcolors.BOLD + 'All done. Have fun!' + bcolors.ENDC)
