import aiohttp
import asyncio
import html
import io
import os
import pathlib
import re
import shutil
import uuid

from . import aioid3, hlscore

from .utils import getLogger, handler
logger = getLogger(name=__name__)
logger.add_handler(handler)

async def download_playlist(playlist):

    album_author = html.unescape(playlist['authorName'])
    album_m = re.match('<a.*?>(.*?)</a>', album_author)
    if album_m:
        album_author = album_m.groups()[0]

    album_title = html.unescape(playlist['title'])
    cover_url = playlist['coverUrl']

    infoLine = playlist['infoLine1']
    info_m = re.match('(.*?)<span.*?></span>(.*?)$', infoLine)
    if info_m:
        genre_ru, year = info_m.groups()
    else:
        year = None

    bcover = None
    if cover_url:
        try:
            await logger.debug(cover_url)
            async with ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
                async with session.get(cover_url) as response:
                    bcover = await response.read()
        except Exception as e:
            await logger.debug(e)

    home = pathlib.Path(os.environ['HOME'])
    album_path = home / 'Music' / 'Musify' / album_author.replace('/', '|') / album_title.replace('/', '|')

    try:
        album_path.mkdir(parents=True)
        tasks = []
        for i, track in enumerate(playlist['list']):
            tasks.append(asyncio.ensure_future(download_track(
                album_path,
                track,
                album_title,
                bcover,
                year,
                i+1,
                playlist['totalCount']
            )))
        await asyncio.gather(*tasks)
        await logger.info(f'Playlist "{album_author} - {album_title}" downloaded successfully.')
    except FileExistsError as e:
        await logger.info(f'Playlist "{album_author} - {album_title}" already exists. Skipping..')
    except BaseException as e:
        await logger.error(f'Playlist "{album_author} - {album_title}" failed to download: {type(e)}: {e}')
        shutil.rmtree(album_path)

async def download_track(album_path, track, album_title, bcover, year, i, n):
    trck = f'{i}/{n}'
    if '.m3u8' in track.decyphered_url:
        try:
            ts_path = album_path / uuid.uuid4().hex
            ts_path.mkdir(exist_ok=True)

            await hlscore.fetch_track(track.decyphered_url, ts_path)
            p = await asyncio.create_subprocess_shell(
                f'ffmpeg -hide_banner -loglevel panic -y -f concat -i {ts_path / "mylist.txt"} -c copy -map 0:a:0 -f mp3 -',
                stdout=asyncio.subprocess.PIPE
            )
            body = await p.stdout.read()
        finally:
            shutil.rmtree(ts_path)
    elif '.mp3' in track.decyphered_url:
        async with aiohttp.ClientSession() as session:
            async with session.get(track.decyphered_url) as response:
                body = await response.read()
    body = io.BytesIO(body)
    body = aioid3.id3(
        body,
        track.performer,
        track.title,
        album_title,
        bcover,
        trck,
        year
    )
    with open(album_path / "{} — {} — {}.mp3".format(
            str(i).zfill(2),
            track.performer.replace('/', '|'),
            track.title.replace('/', '|')
        ), 'wb') as f:
            f.write(body.getvalue())