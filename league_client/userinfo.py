import re

from .logger import logger
from .rso import HEADERS
from .rso import ClientSession
from .rso import get_basic_auth


async def parse_auth_code(session, data, proxy, proxy_auth):
    async with session.post(
        'https://auth.riotgames.com/api/v1/authorization',
        proxy=proxy,
        proxy_auth=proxy_auth,
        json=data,
        headers=HEADERS,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            return
        return res.ok


async def parse_userinfo(session, headers, proxy, proxy_auth):
    async with session.post(
        'https://auth.riotgames.com/userinfo',
        proxy=proxy,
        proxy_auth=proxy_auth,
        json={},
        headers=headers,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            return {'error': 'Failed to parse userinfo'}, 1
        return await res.json(), None


def _extract_tokens(data: str) -> str:
    '''Extract tokens from data'''

    pattern = re.compile(
        'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)'
    )
    response = pattern.findall(data['response']['parameters']['uri'])[0]
    return response


async def parse_access_token(session, data, proxy, proxy_auth):
    async with session.put(
        'https://auth.riotgames.com/api/v1/authorization',
        proxy=proxy,
        proxy_auth=proxy_auth,
        json=data,
        headers=HEADERS,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            return {'error': 'Failed to get access token'}, 1
        data = await res.json()
        response_type = data['type']
        if response_type == 'response':
            logger.info('Parsing userinfo...')
            response = _extract_tokens(data)
            access_token = response[0]
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            data, error = await parse_userinfo(session, headers, proxy, proxy_auth)
            if error:
                logger.info('Failed.')
                return data, 1
            logger.info('Success.')
            return data, None
        elif response_type == 'multifactor':
            return {'error': 'Multifactor authentication'}, 1
        elif response_type == 'auth' and data['error'] == 'auth_failure':
            return {'error': 'Wrong password'}, 1
        elif response_type == 'auth' and data['error'] == 'rate_limited':
            return {'error': 'Rate limited'}, 1
        return {'error': 'Got response type: {response_type}'}, 1

async def get_userinfo(
    username, password, proxy=None, proxy_user=None, proxy_pass=None
):
    try:
        proxy_auth = get_basic_auth(proxy_user, proxy_pass)
        async with ClientSession() as session:
            logger.info('Parsing authorization code...')
            data = {
                'client_id': 'riot-client',
                'nonce': '1',
                'redirect_uri': 'http://localhost/redirect',
                'scope': 'openid ban',
                'response_type': 'token id_token',
            }
            if not await parse_auth_code(session, data, proxy, proxy_auth):
                logger.info('Failed.')
                return {'error': 'Failed to parse authorization code'}, 1
            logger.info('Success.')

            logger.info('Getting access token...')
            data = {
                'type': 'auth',
                'username': username,
                'password': password,
                'remember': True,
            }
            data, error = await parse_access_token(session, data, proxy, proxy_auth)
            if error:
                logger.info('Failed.')
                return data, 1
            logger.info('Success.')
            return data, None
    except Exception as exp:
        logger.error(f'Got exception type: {exp.__class__.__name__}')
        return {'error': 'Exception occurred'}, 1
