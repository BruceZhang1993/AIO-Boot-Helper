import asyncio
import argparse
from pathlib import Path
from .download import get_latest_release, download
from .util import decompress_file
from . import DOWN_FILENAME

async def prepare(args):
    uri = await get_latest_release('nguyentumine', 'AIO-Boot', args.refresh)
    print('Downloading: {}'.format(uri))
    if uri:
        await download(uri, args.overwrite)
    if Path.exists(Path.cwd() / 'aio' / DOWN_FILENAME):
        print('Decompressing: {}'.format(Path.cwd() / 'aio' / DOWN_FILENAME))
        decompress_file(Path.cwd() / 'aio' / DOWN_FILENAME)

async def application(args):
    if args.command:
        await globals().get(args.command)(args)

def main():
    commands = ['prepare']
    parser = argparse.ArgumentParser(description='AIO-Boot Helper')
    parser.add_argument('command', choices=commands, help='Command to use')
    parser.add_argument('--refresh', '-r', action='store_true', default=False, help='Refresh latest release (prepare)')
    parser.add_argument('--overwrite', '-o', action='store_true', default=False, help='Force download file (prepare)')
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application(args))

if __name__ == "__main__":
    main()
