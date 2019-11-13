import asyncio
import argparse
import sys
from pathlib import Path
from .download import get_latest_release, download
from .util import decompress_file, bcolors
from .deploy import deploy_aio
from . import DOWN_FILENAME, ensure_dirs, init_args

async def help(args, parser: argparse.ArgumentParser):
    parser.print_help()

async def prepare(args, _):
    uri = await get_latest_release('nguyentumine', 'AIO-Boot', args.refresh)
    print(bcolors.BOLD + 'Downloading:' + bcolors.ENDC + ' {}'.format(uri))
    if uri:
        await download(uri, args.overwrite)
    if Path.exists(Path.cwd() / 'aio' / DOWN_FILENAME):
        print(bcolors.BOLD + 'Decompressing:' + bcolors.ENDC + ' {}'.format(Path.cwd() / 'aio' / DOWN_FILENAME))
        decompress_file(Path.cwd() / 'aio' / DOWN_FILENAME)

async def deploy(args, _):
    if args.device:
        await deploy_aio(args.device, noask=args.yes, efionly=args.efionly)
    else:
        raise Exception('Please specify devname.')

async def auto_deploy(args, _):
    if not args.device:
        raise Exception('Please specify devname.')
    await prepare(args, _)
    await deploy(args, _)

async def application(args, parser):
    if args.command:
        await globals().get(args.command.replace('-', '_'))(args, parser)

def main():
    try:
        ensure_dirs()
        args, parser = init_args()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(application(args, parser))
    except Exception as e:
        print(bcolors.FAIL + bcolors.BOLD + 'Exception: ' + str(e) + bcolors.UNDERLINE)
        sys.exit(1);

if __name__ == "__main__":
    main()
