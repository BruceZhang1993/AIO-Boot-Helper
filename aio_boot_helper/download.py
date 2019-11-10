import aiohttp
import asyncio
import tqdm
import json
from pathlib import Path
from . import CACHE_LATEST_RELEASE, DOWN_FILENAME, CHUNK_SIZE

GITHUB_API='https://api.github.com/repos/{owner}/{repo}/releases/latest'

async def _get(session, url):
    async with session.get(url) as response:
        return await response.text()

def _parse(data: dict) -> str:
    for asset in data.get('assets'):
        if asset.get('browser_download_url').endswith('.7z'):
            return asset.get('browser_download_url')
    return None

async def get_latest_release(owner, repo, refresh=False):
    if not refresh and Path.exists(CACHE_LATEST_RELEASE):
        print('Latest version cached, add `--refresh` to re-check.')
        with open(CACHE_LATEST_RELEASE, 'r') as f:
            data = json.load(f) 
            return _parse(data)
    else:
        async with aiohttp.ClientSession() as session:
            content = await _get(session, GITHUB_API.format(owner=owner, repo=repo))
            with open(CACHE_LATEST_RELEASE, 'w') as f:
                f.write(content)
            data = json.loads(content)
            return _parse(data)

async def download(uri: str, overwrite=False):
    Path.mkdir(Path.cwd() / 'aio', exist_ok=True)
    if overwrite or not Path.exists(Path.cwd() / 'aio' / DOWN_FILENAME):
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as response:
                length = int(response.headers.get('content-length'))
                pbar = tqdm.tqdm(total=length, unit='B', unit_scale=True)
                with open(Path.cwd() / 'aio' / DOWN_FILENAME, 'wb') as f:
                    while True:
                        chunk = await response.content.read(CHUNK_SIZE)
                        if not chunk:
                            pbar.close()
                            break
                        f.write(chunk)
                        pbar.update(CHUNK_SIZE)
    else:
        print('Downloaded, add `--overwrite` to re-download.')
