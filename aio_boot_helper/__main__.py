import asyncio
import argparse
import sys
from pathlib import Path
from .download import get_latest_release, download
from .util import decompress_file, bcolors
from .deploy import deploy_aio
from . import DOWN_FILENAME

async def help(args, parser: argparse.ArgumentParser):
    parser.print_help()

async def prepare(args, _):
    uri = await get_latest_release('nguyentumine', 'AIO-Boot', args.refresh)
    print('Downloading: {}'.format(uri))
    if uri:
        await download(uri, args.overwrite)
    if Path.exists(Path.cwd() / 'aio' / DOWN_FILENAME):
        print('Decompressing: {}'.format(Path.cwd() / 'aio' / DOWN_FILENAME))
        decompress_file(Path.cwd() / 'aio' / DOWN_FILENAME)

async def deploy(args, _):
    if args.device:
        await deploy_aio(args.device, noask=args.yes)
    else:
        raise Exception('Please specify devname.')

async def auto_deploy(args, _):
    if not args.device:
        raise Exception('Please specify devname.')
    await prepare(args)
    await deploy(args)

async def application(args, parser):
    if args.command:
        await globals().get(args.command.replace('-', '_'))(args, parser)

def main():
    try:
        commands = ['help', 'prepare', 'deploy', 'auto-deploy']
        parser = argparse.ArgumentParser(description='AIO-Boot Helper')
        parser.add_argument('command', choices=commands, help='Command to use')
        parser.add_argument('device', nargs='?', default=None, help='Device to deploy')
        parser.add_argument('--refresh', '-r', action='store_true', default=False, help='Refresh latest release (prepare)')
        parser.add_argument('--overwrite', '-o', action='store_true', default=False, help='Force download file (prepare)')
        parser.add_argument('--yes', '-y', action='store_true', default=False, help='Disable interactive operations [DANGEROUS] (deploy)')
        args = parser.parse_args()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(application(args, parser))
    except Exception as e:
        print(bcolors.FAIL + bcolors.BOLD + 'Exception: ' + str(e) + bcolors.UNDERLINE)
        sys.exit(1);

if __name__ == "__main__":
    main()
