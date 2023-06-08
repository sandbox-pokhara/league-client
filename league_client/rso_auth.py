import aiohttp

from league_client.exceptions import ParseError
from league_client.exceptions import RSOAuthorizeError

from .logger import logger
from .rso import HEADERS
from .rso import get_basic_auth


# ! to deprecate, current_version='1.0.16', Use parse_auth_code instead
async def parsing_auth_code(session, params, proxy, proxy_user=None, proxy_pass=None):
    async with session.get('https://auth.riotgames.com/authorize',
                           params=params,
                           proxy=proxy,
                           proxy_auth=get_basic_auth(proxy_user, proxy_pass),
                           headers=HEADERS) as res:
        if not res.ok:
            logger.debug(res.status)
            return False
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


async def parse_auth_code(session, client_id, scope, proxy=None, proxy_auth=None):
    '''Get auth permit from RSO

    Args:
        session (ClientSession): aiohttp session
        client_id (str): riot client id
        scope (_type_): rso request scope
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        RSOAuthorizeError: AUTH_CODE - Failed to get authorization code
        ParseError
    '''
    data = {
        'acr_values': '',
        'claims': '',
        'client_id': client_id,
        'code_challenge': '',
        'code_challenge_method': '',
        'nonce': 1,
        'redirect_uri': 'http://localhost/redirect',
        'response_type': 'token id_token',
        'scope': scope,
    }
    try:
        async with session.get(
            'https://auth.riotgames.com/authorize',
            params=data,
            proxy=proxy,
            proxy_auth=proxy_auth,
            headers=HEADERS
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise RSOAuthorizeError('Failed to get authorization code', 'AUTH_CODE')
    except (aiohttp.ClientError) as e:
        logger.exception('Failed to parse authorization code')
        raise ParseError('Failed to parse authorization code', 'UNKNOWN') from e
