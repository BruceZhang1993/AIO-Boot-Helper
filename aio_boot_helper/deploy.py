import asyncio
import os

async def run_command(*args):
    process = await asyncio.create_subprocess_exec(
        *args,
        stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode(), process.returncode

async def check_exists(command):
    process = await asyncio.create_subprocess_exec(
        'which', command,
        stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    await process.communicate()
    return process.returncode == 0

async def deploy_grub():
    # if os.geteuid() != 0:
    #     raise Exception('Please run with root permission.')
    command = 'grub-bios-setup'
    if await check_exists(command):
        print('Found: {}'.format(command))
    else:
        raise Exception('Please install grub2.')
    a, b, c = await run_command('ls', '/');
    print(a)
