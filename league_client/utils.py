import re

from .logger import logger
from .rso import HEADERS


# ! deprecated_in='1.0.16', Use rso_tokens._parse_access_token_regex instead
def _extract_tokens(data: str) -> str:
    '''Extract tokens from data'''

    pattern = re.compile(
        r'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)'
    )
    response = pattern.findall(data['response']['parameters']['uri'])[0]
    return response


# ! deprecated_in='1.0.16', Use rso_tokens.parse_auth_access_token instead
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
            response = _extract_tokens(data)
            access_token = response[0]
            return {'access_token': access_token}, None
        elif response_type == 'multifactor':
            return {'error': 'Multifactor authentication'}, 1
        elif response_type == 'auth' and data['error'] == 'auth_failure':
            return {'error': 'Wrong password'}, 1
        elif response_type == 'auth' and data['error'] == 'rate_limited':
            return {'error': 'Rate limited'}, 1
        return {'error': 'Got response type: {response_type}'}, 1


async def parse_blue_essence(session, region, headers, proxy, proxy_auth):
    async with session.get(
        f'https://{region}.store.leagueoflegends.com/storefront/v2/wallet?language=en_GB/',
        proxy=proxy,
        proxy_auth=proxy_auth,
        json={},
        headers=headers,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            return {'error': 'Failed to parse blue essence'}, 1
        return await res.json(), None
