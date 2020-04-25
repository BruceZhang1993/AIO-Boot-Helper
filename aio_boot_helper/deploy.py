import asyncio
import os
import sys
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
    return command, process.returncode == 0

async def get_mount_point(device):
    await asyncio.sleep(1)
    out, _, __ = await run_command('udisksctl', 'info', '-b', device + '1')
    line = list(filter(lambda l: l.find('MountPoints:') >= 0, out.split('\n')))
    return line[0].strip().split()[1]

async def deploy_aio(device, noask=False, efionly=True):
    commands = {
        'udisksctl': 'udisks2',
        'wipefs': 'util-linux',
        'parted': 'parted',
        'pkexec': 'polkit',
    }
    if not efionly:
        commands['grub-install'] = 'grub2'
    check_tasks = [check_exists(k) for k in commands]
    done, _ = await asyncio.wait(check_tasks)
    for task in done:
        command, installed = task.result()
        if installed:
            print(bcolors.BOLD + 'Found:' + bcolors.ENDC + ' {}'.format(command))
        else:
            raise Exception('{} is not found. Please install {}.'.format(command, commands[command]))
    if not noask:
        print(bcolors.WARNING + bcolors.BOLD + '[DANGEROUS] This command will wrap out {}, please BACKUP your data first. \nInput `YES` and press [ENTER] to continue, [Ctrl-C] to abort: '.format(device), end=bcolors.ENDC)
        if input() != "YES":
            raise Exception('User aborted.')
    print('Unmounting device {} ...'.format(device))
    unmount_tasks = []
    unmount_tasks.append(run_command('udisksctl', 'unmount', '-f', '-b', device, allow_fail=True))
    unmount_tasks.append(run_command('udisksctl', 'unmount', '-f', '-b', device + '1', allow_fail=True))
    done, _ = await asyncio.wait(unmount_tasks)
    for task in done:
        out, err, code = task.result()
        if code != 0:
            print(bcolors.WARNING + bcolors.BOLD + err, end=bcolors.ENDC + '\n')
    await run_command('pkexec', 'umount', device, allow_fail=True)
    await run_command('pkexec', 'wipefs', '--all', device)
    await run_command('pkexec', 'parted', device, 'mklabel', 'msdos')
    await run_command('pkexec', 'parted', '--align=opt', device, 'mkpart', 'primary', '0%', '100%')
    await run_command('pkexec', 'mkfs.vfat', '-n', 'AIOBOOT', '-F', '32', device + '1')
    print('Mounting device {} ...'.format(device))
    await asyncio.sleep(3)
    await run_command('udisksctl', 'mount', '-b', device + '1')
    mounting_point = await get_mount_point(device)
    print('Copying AIO files to {} ...'.format(mounting_point))
    files_dir = Path.cwd() / 'aio/aio_latest'
    copyfiles(files_dir, mounting_point)
    if not efionly:
        print('Copying grub files...')
        files_dir = files_dir / 'AIO/grub'
        copyfiles(files_dir, mounting_point + '/boot/grub')
        print('Installing grub2...')
        out, _, __ = await run_command('sudo', 'grub-install', '--target=i386-pc', '--root-directory=' + mounting_point, device)
    print('Unmounting device {} ...'.format(device))
    sync_tasks = [run_command('pkexec', 'sync', device, allow_fail=True), run_command('pkexec', 'sync', device + '1', allow_fail=True)]
    done, _ = await asyncio.wait(sync_tasks)
    for task in done:
        if code != 0:
            print(bcolors.WARNING + bcolors.BOLD + err, end=bcolors.ENDC + '\n')
    await run_command('udisksctl', 'unmount', '-f', '-b', device + '1', allow_fail=True)
    print(bcolors.OKGREEN + bcolors.BOLD + 'All done. Have fun!' + bcolors.ENDC)
