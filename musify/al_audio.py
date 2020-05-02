import aiohttp
from functools import wraps

def get(func):
    @wraps(func)
    async def inner(session, fake, *args, **kwargs):
        url = func(*args, **kwargs)
        headers = {'Cookie': 'remixsid={}'.format(fake['cookie'])}
        async with session.get(url, headers=headers) as response:
            return await response.text()
    return inner


def post(func):
    @wraps(func)
    async def inner(session, fake, *args, **kwargs):
        url, data = func(*args, **kwargs)
        headers = {'Cookie': 'remixsid={}'.format(fake['cookie'])}
        async with session.post(url, headers=headers, data=data) as response:
            return await response.text()
    return inner

@post
def load_section(
    owner_id, 
    playlist_id, 
    access_hash,
    offset=0,
    _type='playlist'
):
        url = 'https://vk.com/al_audio.php'
        data = {'act': 'load_section',
                'owner_id': owner_id,
                'playlist_id': playlist_id,
                'offset': offset,
                'type': 'playlist',
                'al': 1,
                'access_hash': access_hash,
                'is_loading_all': 0}
        return url, data

@post
def reload_audio(ids):
    url = 'https://vk.com/al_audio.php'
    data = {'act': 'reload_audio',
            'al': 1,
            'ids': ids}
    return url, data