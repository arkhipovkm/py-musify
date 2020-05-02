from aiohttp import ClientSession
import re

import logging
logger = logging.getLogger(__name__)

LOGIN_URL = 'https://login.vk.com/?act=login'

async def get_remixsid(login, password, sem=None):
    async with ClientSession() as session:
        async with session.get('https://vk.com') as response:
            body = await response.text()
            ip_h, lg_h = re.search('&ip_h=(.*?)&lg_h=(.*?)&', body).groups()
        data = {
            'act': 'login',
            'email': login,
            'pass': password,
            'ip_h': ip_h,
            'lg_h': lg_h,
            'captcha_sid': '',
            'captcha_key': '',
            'expire': '',
            'role': 'al_frame',
        }
        async with session.post(LOGIN_URL, data=data) as response:
            cookie = session.cookie_jar._cookies['vk.com']['remixsid']
            v = cookie.value
            exp = cookie['expires']
    if sem:
        sem.release()
        logger.debug(f'Released semaphore..')
    return v