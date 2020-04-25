import asyncio
import argparse
import sys
from pathlib import Path
from .download import get_latest_release, download
from .util import decompress_file, bcolors
from .deploy import deploy_aio
from . import DOWN_FILENAME, ensure_dirs, init_args

async def help(args: argparse.Namespace, parser: argparse.ArgumentParser):
    """Print help information

    :param args: Arguments
    :type args: argparse.Namespace
    :param parser: Argument parser instance
    :type parser: argparse.ArgumentParser
    """
    parser.print_help()

async def prepare(args: argparse.Namespace, parser: argparse.ArgumentParser):
    """Download AIOBOOT and decompress

    :param args: Arguments
    :type args: argparse.Namespace
    :param parser: Argument parser instance
    :type parser: argparse.ArgumentParser
    """
    data = await get_latest_release('nguyentumine', 'AIO-Boot', True)
    print(bcolors.BOLD + 'Downloading:' + bcolors.ENDC + ' {}'.format(data.get('uri')))
    if data:
        await download(data, args.overwrite)
    if Path.exists(Path.cwd() / 'aio' / DOWN_FILENAME):
        print(bcolors.BOLD + 'Decompressing:' + bcolors.ENDC + ' {}'.format(Path.cwd() / 'aio' / DOWN_FILENAME))
        decompress_file(Path.cwd() / 'aio' / DOWN_FILENAME)

async def deploy(args: argparse.Namespace, _):
    """Deploy AIOBOOT to device

    :param args: Arguments
    :type args: argparse.Namespace
    :raises Exception: Raises exception if device argument is missing
    """
    if args.device:
        await deploy_aio(args.device, noask=args.yes, efionly=args.efionly)
    else:
        raise Exception('Please specify devname.')

async def auto_deploy(args: argparse.Namespace, parser: argparse.ArgumentParser):
    """Prepare and deploy AIOBOOT to device

    :param args: Arguments
    :type args: argparse.Namespace
    :param parser: Argument parser instance
    :type parser: argparse.ArgumentParser
    :raises Exception: Raises exception if device argument is missing
    """
    if not args.device:
        raise Exception('Please specify devname.')
    await prepare(args, parser)
    await deploy(args, parser)

async def application(args: argparse.Namespace, parser: argparse.ArgumentParser):
    """Application entry to dispatch command to functions

    :param args: Arguments
    :type args: argparse.Namespace
    :param parser: Argument parser instance
    :type parser: argparse.ArgumentParser
    """
    if args.command:
        await globals().get(args.command.replace('-', '_'))(args, parser)

def main():
    """Main entry"""
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
