import aiohttp
import html
import json
import os
import re
import pathlib
import urllib.parse

from .al_audio import load_section, reload_audio
from .al_audio_object import AlAudioObject
from .crypto import decypher

from .utils import getLogger, handler
logger = getLogger(name=__name__)
logger.add_handler(handler)

class PlaylistExists(Exception):
    pass

def _get_json_payload(resp):
    return json.loads(re.search('<!--(.*?)$', resp).groups()[0], strict=False)['payload'][1][0]

async def get_playlist(id, fake):
    try:
        owner_id, playlist_id, access_hash = id.split('_')
    except ValueError:
        owner_id, playlist_id = id.split('_')
        access_hash = ''
        
    async with aiohttp.ClientSession() as session:
        resp = await load_section(session, fake, owner_id, playlist_id, access_hash)
        resp = urllib.parse.unquote(resp)
        playlist = _get_json_payload(resp)

        album_author = html.unescape(playlist['authorName'])
        album_m = re.match('<a.*?>(.*?)</a>', album_author)
        if album_m:
            album_author = album_m.groups()[0]
        album_title = html.unescape(playlist['title'])
        home = pathlib.Path(os.environ['HOME'])
        album_path = home / 'Music' / 'Musify' / album_author.replace('/', '|') / album_title.replace('/', '|')

        if album_path.exists():
            await logger.info(f'Playlist "{album_author} - {album_title}" already exists. Skipping..')
            raise PlaylistExists

        audio_ids = []
        playlist['list'] = [AlAudioObject(a) for a in playlist['list']]
        for audio in playlist['list']:
            audio_ids.append('{}_{}_{}'.format(audio.fullId, audio.actionHash, audio.urlHash))
        for i in range(0, len(audio_ids), 10):
            ids = ','.join(audio_ids[i:i+10])
            resp = await reload_audio(session, fake, ids)
            raw_audio_objects = _get_json_payload(resp)
            audio_objects = [
                AlAudioObject(x) for x in raw_audio_objects
            ]
            audio_objects_index = {x.fullId: x for x in audio_objects}
            for audio in playlist['list']:
                if audio.fullId in audio_objects_index.keys():
                    audio.url = audio_objects_index[audio.fullId].url
                    audio.decyphered_url = decypher(audio.url, fake['id'])
    return playlist