import asyncio
import os

from musify.login import get_remixsid
from musify.core import get_playlist, PlaylistExists
from musify.download import download_playlist

async def main():
    fake = dict(
        id=os.environ['MUSIFY_ID']
    )
    fake['cookie'] = await get_remixsid(os.environ['MUSIFY_USERNAME'], os.environ['MUSIFY_PASSWORD'])
    with open('urls.txt', 'r') as f:
        urls = f.readlines()
    ids = [
        x.split('/')[-1].strip('\n') for x in urls
    ]
    for _id in ids:
        try:
            pl = await get_playlist(
                _id,
                fake
            )
        except PlaylistExists:
            continue
        await asyncio.ensure_future(download_playlist(pl))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    pass