import os
import io
import urllib.parse
from aiohttp import ClientSession

import mutagen.id3

try:
    LASTFM_TOKEN = os.environ['LASTFM_TOKEN']
except KeyError:
    LASTFM_TOKEN = ""

from .utils import getLogger, handler
logger = getLogger(name=__name__)
logger.add_handler(handler)

def png2jpg(bcover):
    from PIL import Image
    with io.BytesIO(bcover) as bi:
        im = Image.open(bi)
        cim = im.convert(mode='RGB')
    with io.BytesIO() as bo:
        cim.save(bo, format='jpeg')
        return bo.getvalue()



async def last_fm(performer, title):
     URL = 'https://ws.audioscrobbler.com/2.0/?{}'
     params = {'method': 'track.getInfo',
               'api_key': LASTFM_TOKEN,
               'artist': performer,
               'track': title,
               'format': 'json',
               'autocorrect': 1}
     url = URL.format(urllib.parse.urlencode(params))
     async with ClientSession() as session:
        async with session.get(url) as response:
            js = await response.json()
            try:
                album = js['track']['album']['title']
                cover_url = js['track']['album']['image'][-1]['#text']
                try:
                    async with session.get(cover_url) as response:
                        bcover = await response.read()
                except Exception as e:
                    await logger.error(e)
                    bcover = None
                await logger.debug(f'{album} : {cover_url}')
                return album, bcover
            except KeyError as e:
                await logger.debug(f'KeyError: {e}. {js}')
                return None, None


def id3(bobj, performer, title, album, bcover, trck, tyer, is_png=False):
    try:
        tags = mutagen.id3.ID3(fileobj=bobj)
    except mutagen.id3.ID3NoHeaderError:
        tags = mutagen.id3.ID3()
    tags.clear()
    tags.add(mutagen.id3.TPE1(encoding=3, text=performer))
    tags.add(mutagen.id3.TIT2(encoding=3, text=title))
    tags.add(mutagen.id3.TCOP(encoding=3, text='Vk Music via Musify'))
    tags.add(mutagen.id3.TRCK(encoding=3, text=trck))
    if tyer:
        tags.add(mutagen.id3.TYER(encoding=3, text=tyer))
    if bcover:
        bcover = png2jpg(bcover) if is_png else bcover
        tags.add(mutagen.id3.APIC(3, 'image/jpg', 3, 'FRONT_COVER', bcover))
    if album:
        tags.add(mutagen.id3.TALB(encoding=3, text=album))
    tags.save(fileobj=bobj)
    return bobj
