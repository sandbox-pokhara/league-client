import json
import re
from base64 import urlsafe_b64decode
from urllib.parse import urljoin

import aiohttp

from league_client.exceptions import LeagueEdgeError
from league_client.exceptions import ParseError
from league_client.exceptions import RSOAuthorizeError

from .logger import logger
from .rso import HEADERS

PLAYER_PLATFORM_MAPPING = {
    'EUW1': 'euc1',
    'EUN1': 'euc1',
    'NA1': 'usw2',
    'LA1': 'usw2',
    'LA2': 'usw2',
    'TR1': 'euc1',
    'RU': 'euc1',
    'OC1': 'usw2',
    'BR1': 'usw2',
    'JP1': 'apne1',
    'SG2': 'apse1',
}

LEDGE_URL_MAPPING = {
    'BR1': 'br',
    'EUN1': 'eune',
    'EUW1': 'euw',
    'JP1': 'jp',
    'LA1': 'lan',
    'LA2': 'las',
    'NA1': 'na',
    'OC1': 'oce',
    'RU': 'ru',
    'TR1': 'tr',
}

LOCATION_PARAMETERS = {
    "BR1": "lolriot.mia1.br1",
    "EUN1": "lolriot.euc1.eun1",
    "EUW1": "lolriot.ams1.euw1",
    "JP1": "lolriot.nrt1.jp1",
    "LA1": "lolriot.mia1.la1",
    "LA2": "lolriot.mia1.la2",
    "NA1": "lolriot.pdx2.na1",
    "OC1": "lolriot.pdx1.oc1",
    "RU": "lolriot.euc1.ru",
    "TR1": "lolriot.euc1.tr1",
}


# ! deprecated_in='1.0.16', Use _parse_access_token_regex instead
def _extract_tokens(data: str) -> str:
    '''Extract tokens from data'''

    pattern = re.compile(
        r'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)'
    )
    response = pattern.findall(data['response']['parameters']['uri'])[0]
    return response


# ! deprecated_in='1.0.16', Use parse_auth_access_token instead
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


def _parse_access_token_regex(data):
    '''Extract access token from data

    Args:
        data (dict): response json from authorization request

    Raises:
        ParseError

    Returns:
        str: parsed access token
    '''

    try:
        pattern = re.compile(
            r'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)'
        )
        token = pattern.findall(data['response']['parameters']['uri'])[0][0]
        return token
    except (re.error, KeyError, IndexError) as e:
        logger.exception('Failed to parse tokens (regex)')
        raise ParseError('Failed to parse tokens (regex)') from e


async def parse_auth_access_token(session, username, password, proxy=None, proxy_auth=None):
    '''Parse access token from authorization credentials

    Args:
        session (league_client.rso.ClentSession): aiohttp session
        username (str): account username
        username (str): account password
        proxy (str, optional): proxy url
        proxy_auth (BasicAuth, optional): proxy auth(username, password)

    Raises:
        RSOAuthorizeError: ACCESS_TOKEN - Failed to get access token
        RSOAuthorizeError: MULTIFACTOR - Account has multifactor auth enabled
        RSOAuthorizeError: WRONG_PASSWORD - Password is incorrect
        RSOAuthorizeError: RATE_LIMITED - Rate limited by RSO, use proxy

        ParseError

    Returns:
        str: access_token
    '''
    data = {
        'type': 'auth',
        'username': username,
        'password': password,
        'remember': True,
    }
    try:
        async with session.put(
            'https://auth.riotgames.com/api/v1/authorization',
            proxy=proxy,
            proxy_auth=proxy_auth,
            json=data,
            headers=HEADERS,
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise RSOAuthorizeError('Failed to get access token', 'ACCESS_TOKEN')
            data = await res.json()
            response_type = data['type']
            if response_type == 'response':
                access_token = _parse_access_token_regex(data)
                return access_token
            elif response_type == 'multifactor':
                raise RSOAuthorizeError('Multifactor authentication', 'MULTIFACTOR')
            elif response_type == 'auth' and data['error'] == 'auth_failure':
                raise RSOAuthorizeError('Wrong password', 'WRONG_PASSWORD')
            elif response_type == 'auth' and data['error'] == 'rate_limited':
                raise RSOAuthorizeError('Rate limited', 'RATE_LIMITED')
            raise RSOAuthorizeError(f'Got response type: {response_type}', 'UNKNOWN')
    except (aiohttp.ClientError, ValueError, KeyError) as e:
        logger.exception('Failed to parse access token')
        raise ParseError('Failed to parse access token', 'UNKNOWN') from e


async def parse_entitlements_token(session, access_token, proxy=None, proxy_auth=None):
    '''Parse entitlements token using access token

    Args:
        session (league_client.rso.ClentSession): aiohttp session
        access_token (str): access token
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        RSOAuthorizeError: ENTITLEMENTS_TOKEN - Failed to get entitlements token
        ParseError

    Returns:
        str: entitlements token
    '''
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    try:
        async with session.post(
            "https://entitlements.auth.riotgames.com/api/token/v1",
            headers=headers,
            proxy=proxy,
            proxy_auth=proxy_auth,
            json={},
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise RSOAuthorizeError('Failed to get entitlements token', 'ENTITLEMENTS_TOKEN')
            return (await res.json())['entitlements_token']
    except (aiohttp.ClientError, ValueError, KeyError) as e:
        logger.exception('Failed to parse entitlements token')
        raise ParseError('Failed to parse entitlements token', 'UNKNOWN') from e


async def get_tokens(
        session, username, password,
        proxy=None, proxy_auth=None,
        client_id='lol',
        scope='openid offline_access lol ban profile email phone birthdate lol_region',
        entitlement=False
):
    '''Authorize RSO and get access token and entitlements token(optional)

    Args:
        session (league_client.rso.ClentSession): aiohttp session
        username (str): account username
        password (str): account password
        proxy (str, optional): proxy url. Defaults to None.
        proxy_user (str, optional): proxy username. Defaults to None.
        proxy_pass (str, optional): proxy password. Defaults to None.
        client_id (str, optional): riot client id. Defaults to 'lol'.
        scope (str, optional): rso request scope. Defaults to 'openid offline_access lol ban profile email phone birthdate lol_region'.
        entitlement (bool, optional): whether to parse entitlements token or not. Defaults to False.

    Raises:
        RSOAuthorizeError: AUTH_CODE - Failed to parse authorization code
        RSOAuthorizeError: ACCESS_TOKEN - Failed to parse access token
        RSOAuthorizeError: ENTITLEMENTS_TOKEN - Failed to parse entitlements token

        RSOAuthorizeError: MULTIFACTOR - Account has multifactor auth enabled
        RSOAuthorizeError: WRONG_PASSWORD - Password is incorrect
        RSOAuthorizeError: RATE_LIMITED - Rate limited by Riot, use proxy

    Returns:
        dict:
            access_token (str): access token
            entitlements_token (str, optional): entitlements token
    '''
    access_token = entitlements_token = None
    await parse_auth_code(session, client_id, scope, proxy, proxy_auth)
    access_token = await parse_auth_access_token(session, username, password, proxy, proxy_auth)
    if entitlement:
        entitlements_token = await parse_entitlements_token(session, access_token, proxy, proxy_auth)
    return {'access_token': access_token, 'entitlements_token': entitlements_token}


def parse_info_from_access_token(access_token):
    '''Parse info from access token

    Args:
        access_token (str): access token

    Raises:
        ParseError

    Returns:
        dict:
            puuid (str): player uuid
            account_id (str): account id
            region (str): region
    '''
    try:
        payload = access_token.split(".")[1]
        info = urlsafe_b64decode(f'{payload}===')
        data = json.loads(info)
        return {
            'puuid': data['sub'],
            'account_id': data['dat']['u'],
            'region': data['dat']['r']

        }
    except (ValueError, KeyError, IndexError, TypeError) as e:
        logger.exception('Failed to parse info from access token')
        raise ParseError('Failed to parse info from access token') from e


async def parse_userinfo(session, access_token, proxy=None, proxy_auth=None, parse_token=False):
    '''Get userinfo from RSO

    Args:
        session (league_client.rso.ClientSession): aiohttp session
        access_token (str): access token
        parse_token (bool, optional): whether to return token(str) or userinfo. Defaults to False.
                                    if False, returns userinfo. if True, returns token
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        RSOAuthorizeError: USERINFO - Failed to get userinfo
        ParseError

    Returns:
        dict: 'info': (dict or None)
                        'country': (str) country code
                        'sub': (str) player sub id
                        'summoner_name': (str) summoner name
                        'summoner_id': (str) summoner id
                        'summoner_level': (int) summoner level
                        'password_changed_at': (int) epoch time in milliseconds
                        'email_verified': (bool) whether email is verified or not
                        'phone_number_verified': (bool) whether phone number is verified or not
                        'ban_status': (dict) ban status 'restrictions': (list) list of restrictions
                        'region': (str) region
                        'game_name': (str) game name
            'token': (str or None) token (if parse_token=True)
    '''
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }
    info_res = token_res = None
    try:
        async with session.post(
            'https://auth.riotgames.com/userinfo',
            proxy=proxy,
            proxy_auth=proxy_auth,
            json={},
            headers=headers,
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise RSOAuthorizeError('Failed to get userinfo', 'USERINFO')
            if (not parse_token):
                userinfo = await res.json()
                info_res = {
                    'country': userinfo['country'],
                    'sub': userinfo['sub'],
                    'summoner_name': userinfo['lol_account']['summoner_name'],
                    'summoner_id': userinfo['lol_account']['summoner_id'],
                    'summoner_level': userinfo['lol_account']['summoner_level'],
                    'password_changed_at': userinfo['pw']['cng_at'],
                    'email_verified': userinfo['email_verified'],
                    'phone_number_verified': userinfo['phone_number_verified'],
                    'username': userinfo['username'],
                    'ban_stats': userinfo['ban'],
                    'region': userinfo['region']['tag'],
                    'game_name': userinfo['acct']['game_name'],
                }
            else:
                token_res = await res.text()
            return {'info': info_res, 'token': token_res}
    except (aiohttp.ClientError, ValueError, KeyError, TypeError) as e:
        logger.exception('Failed to parse userinfo')
        raise ParseError('Failed to parse userinfo', 'UNKNOWN') from e


async def create_login_queue(session, region, tokens, userinfo_token, proxy=None, proxy_auth=None):
    '''Create login queue

    Args:
        session (league_client.rso.ClientSession): aiohttp session
        region (str): region
        entitlements_token (str): entitlements token
        userinfo_token (str): userinfo_token
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        LeagueEdgeError: LOGIN_QUEUE - Failed to create login queue
        ParseError

    Returns:
        str: login queue token
    '''
    try:
        pp_url = f'https://{PLAYER_PLATFORM_MAPPING[region]}-green.pp.sgp.pvp.net'
        data = {
            "clientName": "lcu",
            "entitlements": tokens['entitlements_token'],
            "userinfo": userinfo_token,
        }
        headers = {
            'Authorization': f'Bearer {tokens["access_token"]}',
        }
        async with session.post(
            urljoin(pp_url, f'login-queue/v2/login/products/lol/regions/{region}'),
            proxy=proxy,
            proxy_auth=proxy_auth,
            json=data,
            headers=headers
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise LeagueEdgeError('Failed to create login queue', 'LOGIN_QUEUE')
            return (await res.json())['token']
    except (aiohttp.ClientError, ValueError, KeyError) as e:
        logger.exception('Failed to create login queue')
        raise ParseError('Failed to create login queue', 'UNKNOWN') from e


async def create_login_session(session, region, login_queue_token, puuid, proxy=None, proxy_auth=None):
    '''Create login session

    Args:
        session (league_client.rso.ClientSession): aiohttp session
        region (str): region
        login_queue_token (str): login queue token
        puuid (str): player uuid
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        LeagueEdgeError: LOGIN_SESSION - Failed to create login session
        ParseError

    Returns:
        str: league edge token
    '''
    try:
        pp_url = f'https://{PLAYER_PLATFORM_MAPPING[region]}-green.pp.sgp.pvp.net'
        data = {
            "claims": {
                "cname": "lcu"
            },
            "product": "lol",
            "puuid": puuid,
            "region": region.lower(),
        }
        headers = {
            'Authorization': f'Bearer {login_queue_token}',
        }
        async with session.post(
            urljoin(pp_url, 'session-external/v1/session/create'),
            proxy=proxy,
            proxy_auth=proxy_auth,
            json=data,
            headers=headers
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise LeagueEdgeError('Failed to create login session', 'LOGIN_SESSION')
            return await res.json()
    except (aiohttp.ClientError, ValueError, KeyError) as e:
        logger.exception('Failed to create login session')
        raise ParseError('Failed to create login session', 'UNKNOWN') from e


async def parse_ledge_token(session, account_info, tokens, proxy=None, proxy_auth=None):
    '''Parse league edge auth token

    Args:
        session (league_client.rso.ClientSession): aiohttp session
        account_info (dict): account info {'region': '...', 'puuid': '...'}
        tokens (dict): tokens {'access_token': '...', 'entitlements_token': '...'}
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        RSOAuthorizeError: USERINFO - Failed to get userinfo

        LeagueEdgeError: LOGIN_QUEUE - Failed to create login queue
        LeagueEdgeError: LOGIN_SESSION - Failed to create login session

        ParseError

    Returns:
        str: ledge token
    '''
    try:
        region = account_info['region']
        puuid = account_info['puuid']
        access_token = tokens['access_token']
        userinfo = await parse_userinfo(session, access_token, proxy, proxy_auth, parse_token=True)
        login_queue_token = await create_login_queue(session, region, tokens, userinfo['token'], proxy, proxy_auth)
        ledge_token = await create_login_session(session, region, login_queue_token, puuid, proxy, proxy_auth)
    except KeyError as e:
        logger.exception('Failed to parse ledge token')
        raise ParseError('Failed to parse ledge token', 'UNKNOWN') from e
    return ledge_token


async def get_owned_skins(session, account_info, ledge_token, proxy=None, proxy_auth=None):
    '''Get owned skins

    Args:
        session (league_client.rso.ClientSession): aiohttp session
        account_info (dict): account info {'region': '...', 'puuid': '...', 'account_id': '...'}
        ledge_token (str): ledge token
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        LeagueEdgeError: OWNED_SKINS - Failed to get owned skins

        ParseError

    Returns:
        list: owned skins id [int, ...]
    '''
    try:
        region = account_info['region']
        puuid = account_info['puuid']
        account_id = account_info['account_id']
        url = f"https://{LEDGE_URL_MAPPING[region]}-red.lol.sgp.pvp.net/lolinventoryservice-ledge/v1/inventories/simple?puuid={puuid}&location={LOCATION_PARAMETERS[region]}&accountId={account_id}&inventoryTypes=CHAMPION_SKIN"
        headers = {
            'Authorization': f'Bearer {ledge_token}',
        }
        async with session.get(
            url,
            proxy=proxy,
            proxy_auth=proxy_auth,
            json={},
            headers=headers
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise LeagueEdgeError('Failed to get owned skins', 'OWNED_SKINS')
            owned_skins = (await res.json())['data']['items']['CHAMPION_SKIN']
            return owned_skins
    except (aiohttp.ClientError, ValueError, KeyError, TypeError) as e:
        logger.exception('Failed to get owned skins')
        raise ParseError('Failed to get owned skins', 'UNKNOWN') from e


async def get_loot(session, account_info, ledge_token, proxy=None, proxy_auth=None):
    '''Get loot info (champion shards, skin shards, essence)

    Args:
        session (league_client.rso.ClientSession): aiohttp session
        account_info (dict): account info {'region': '...', 'account_id': '...'}
        ledge_token (str): ledge token
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        LeagueEdgeError: LOOT_STATS - Failed to get loot stats

        ParseError

    Returns:
        dict: 'blue_essence', 'orange_essence', 'mythic_esence', 'normal_skins', 'permanent_skins'
    '''
    try:
        region = account_info['region']
        account_id = account_info['account_id']
        url = f'https://{LEDGE_URL_MAPPING[region]}-red.lol.sgp.pvp.net/loot/v1/playerlootdefinitions/location/{LOCATION_PARAMETERS[region]}/playerId/{account_id}'
        headers = {
            'Authorization': f'Bearer {ledge_token}',
        }
        async with session.get(
            url,
            proxy=proxy,
            proxy_auth=proxy_auth,
            json={},
            headers=headers
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise LeagueEdgeError('Failed to get loot stats', 'LOOT_STATS')
            loot = (await res.json())['playerLoot']
            blue_essence = next(
                filter(
                    lambda item: 'CURRENCY_champion' in item['lootName'],
                    loot),
                None)['count']
            orange_essence = next(
                filter(
                    lambda item: 'CURRENCY_cosmetic' in item['lootName'],
                    loot),
                None)['count']
            mythic_essence = next(
                filter(
                    lambda item: 'CURRENCY_mythic' in item['lootName'],
                    loot),
                None)['count']
            all_skins = [item['lootName']
                         for item in list(
                             filter(lambda item: 'CHAMPION_SKIN_' in item['lootName'],
                                    loot))]
            normal_skins = list(filter(lambda item: 'CHAMPION_SKIN_RENTAL' in item, all_skins))
            perm_skins = list(filter(lambda item: item not in normal_skins, all_skins))
            if normal_skins:
                normal_skins = [int(item.split("CHAMPION_SKIN_RENTAL_")[1])
                                for item in normal_skins]
            if perm_skins:
                perm_skins = [int(item.split("CHAMPION_SKIN_")[1]) for item in perm_skins]
            return {
                'blue_essence': blue_essence,
                'orange_essence': orange_essence,
                'mythic_essence': mythic_essence,
                'normal_skins': normal_skins,
                'permanent_skins': perm_skins,
            }
    except (aiohttp.ClientError, ValueError, KeyError, IndexError, TypeError) as e:
        logger.exception('Failed to get loot stats')
        raise ParseError('Failed to get loot stats', 'UNKNOWN') from e


async def get_honor_level(session, account_info, ledge_token, proxy=None, proxy_auth=None):
    '''Get honor level

    Args:
        session (league_client.rso.ClientSession): aiohttp session
        account_info (dict): account info {'region': '...'}
        ledge_token (str): ledge token
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        LeagueEdgeError: HONOR_LEVEL - Failed to get honor level

        ParseError

    Returns:
        dict or None: honor level info {'honorLevel':int, 'checkpoint':int, 'rewardsLocked':bool}
    '''
    try:
        region = account_info['region']
        url = f'https://{LEDGE_URL_MAPPING[region]}-red.lol.sgp.pvp.net/honor-edge/v2/retrieveProfileInfo/'
        headers = {
            'Authorization': f'Bearer {ledge_token}',
        }
        async with session.get(
            url,
            proxy=proxy,
            proxy_auth=proxy_auth,
            json={},
            headers=headers
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise LeagueEdgeError('Failed to get honor level', 'HONOR_LEVEL')
            return await res.json()
    except (aiohttp.ClientError, ValueError, KeyError) as e:
        logger.exception('Failed to get honor level')
        raise ParseError('Failed to get honor level', 'UNKNOWN') from e


async def get_rank_info(session, account_info, ledge_token, proxy=None, proxy_auth=None):
    '''Get rank info

    Args:
        session (league_client.rso.ClientSession): aiohttp session
        account_info (dict): account info {'region': '...', 'puuid': '...'}
        ledge_token (str): ledge token
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        LeagueEdgeError: RANK_INFO - Failed to get rank info
        ParseError: _description_

    Returns:
        dict: {'queue': 'RANKED_SOLO_5x5', 'tier': str, 'division': str, 'wins': int, 'losses': int}
    '''
    try:
        region = account_info['region']
        puuid = account_info['puuid']
        url = f'https://{LEDGE_URL_MAPPING[region]}-red.lol.sgp.pvp.net/leagues-ledge/v2/rankedStats/puuid/{puuid}'
        headers = {
            'Authorization': f'Bearer {ledge_token}',
        }
        async with session.get(
            url,
            proxy=proxy,
            proxy_auth=proxy_auth,
            json={},
            headers=headers
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise LeagueEdgeError('Failed to get rank info', 'RANK_INFO')
            rank = (await res.json())['queues'][0]
            return {
                'queue': rank['queueType'],  # 'RANKED_SOLO_5x5
                'tier': rank.get('tier', 'UNRANKED'),
                'division': rank.get('rank'),
                'wins': rank['wins'],
                'losses': rank['losses'],
            }
    except (aiohttp.ClientError, ValueError, KeyError, IndexError) as e:
        logger.exception('Failed to get rank info')
        raise ParseError('Failed to get rank info', 'UNKNOWN') from e
