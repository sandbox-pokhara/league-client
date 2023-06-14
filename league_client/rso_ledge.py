from urllib.parse import urljoin

import aiohttp

from league_client.exceptions import LeagueEdgeError
from league_client.exceptions import ParseError
from league_client.rso_userinfo import parse_userinfo

from .logger import logger

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
        account_info (dict): account info {'region': '...', 'summoner_id': '...'}
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
        summoner_id = account_info['summoner_id']
        url = f'https://{LEDGE_URL_MAPPING[region]}-red.lol.sgp.pvp.net/loot/v1/playerlootdefinitions/location/{LOCATION_PARAMETERS[region]}/playerId/{summoner_id}'
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
