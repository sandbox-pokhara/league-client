from .logger import logger
from .rso import HEADERS
from .rso import get_basic_auth


async def parsing_auth_code(session, params, proxy, proxy_user=None, proxy_pass=None):
    async with session.get('https://auth.riotgames.com/authorize',
                           params=params,
                           proxy=proxy,
                           proxy_auth=get_basic_auth(proxy_user, proxy_pass),
                           headers=HEADERS) as res:
        if not res.ok:
            logger.debug(res.status)
            return
        return res.ok


async def rso_auth(session, username, password, proxy, proxy_user=None, proxy_pass=None):
    data = {
        'type': 'auth',
        'username': username,
        'password': password,
        'remember': True,
        'language': 'en_US',
    }
    async with session.put('https://auth.riotgames.com/api/v1/authorization',
                           proxy=proxy,
                           proxy_auth=get_basic_auth(proxy_user, proxy_pass),
                           json=data,
                           headers=HEADERS) as res:
        if not res.ok:
            logger.debug(res.status)
            logger.debug(await res.text())
            return None
        data = await res.json()
        if data['type'] != 'response':
            logger.debug(data)
            return None
        try:
            return data['response']['parameters']['uri']
        except KeyError:
            logger.debug(data)
            return None
