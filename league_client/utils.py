import re
from .logger import logger
from .rso import HEADERS


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