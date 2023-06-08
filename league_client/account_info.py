import aiohttp

from league_client.rso import get_basic_auth
from league_client.rso_ledge import get_honor_level
from league_client.rso_ledge import get_loot
from league_client.rso_ledge import get_owned_skins
from league_client.rso_ledge import get_rank_info
from league_client.rso_ledge import parse_ledge_token
from league_client.rso_tokens import get_tokens
from league_client.rso_tokens import parse_info_from_access_token
from league_client.rso_userinfo import parse_userinfo


async def get_account_info(
    username, password,
    user_info=True, skins=True,
    honor_level=True, rank_info=True,
    proxy=None, proxy_user=None, proxy_pass=None
):
    '''Get account info.

    Args:
        username (str): account username
        password (str): account password
        user_info (bool, optional): whether to parse user_info. Defaults to True.
        skins (bool, optional): whether to parse skins_info. Defaults to True.
        honor_level (bool, optional): whether to parse honor_info. Defaults to True.
        rank_info (bool, optional): whether to parse rank_info. Defaults to True.
        proxy (str, optional): proxy url. Defaults to None.
        proxy_user (str, optional): proxy username. Defaults to None.
        proxy_pass (str, optional): proxy password. Defaults to None.

    Returns:
        dict: 'user_info': {'summoner_level', 'summoner_name', 'email_verified', 'phone_number_verified', 'ban_stats', ...} or None,
            'account_info': {'puuid', 'region', ...} or None,
            'essence_info': {'blue_essence', 'orange_essence', 'mythic_essence'} or None,
            'skins_info': {'owned_skins', 'normal_skins', 'permanent_skins'} or None,
            'honor_info': {'honor_level', ...} or None,
            'rank_info': {'rank', 'tier', 'wins', 'losses', ...} or None,
    '''
    owned_skins_res = loot_res = honor_level_res = rank_info_res = tokens = account_info = normal_skins = permanent_skins = blue_essence = orange_essence = mythic_essence = None
    userinfo = {}
    proxy_auth = get_basic_auth(proxy_user, proxy_pass)
    if user_info:
        async with aiohttp.ClientSession() as session:
            tokens = await get_tokens(session, username, password, proxy, proxy_auth, client_id='riot-client')
            userinfo = await parse_userinfo(session, tokens['access_token'], proxy, proxy_auth, parse_token=False)
    if (skins or honor_level or rank_info):
        async with aiohttp.ClientSession() as session:
            tokens = await get_tokens(session, username, password, proxy, proxy_auth, client_id='lol', entitlement=True)
            account_info = parse_info_from_access_token(tokens['access_token'])
            ledge_token = await parse_ledge_token(session, account_info, tokens, proxy, proxy_auth)
            if skins:
                owned_skins_res = await get_owned_skins(session, account_info, ledge_token, proxy=None, proxy_auth=None)
                loot_res = await get_loot(session, account_info, ledge_token, proxy=None, proxy_auth=None)
                blue_essence = loot_res['blue_essence']
                orange_essence = loot_res['orange_essence']
                mythic_essence = loot_res['mythic_essence']
                normal_skins = loot_res['normal_skins']
                permanent_skins = loot_res['permanent_skins']
            if honor_level:
                honor_level_res = await get_honor_level(session, account_info, ledge_token, proxy=None, proxy_auth=None)
            if rank_info:
                rank_info_res = await get_rank_info(session, account_info, ledge_token, proxy=None, proxy_auth=None)
    return {
        'user_info': userinfo.get('info'),
        'account_info': account_info,
        'essence_info': {
            'blue_essence': blue_essence,
            'orange_essence': orange_essence,
            'mythic_essence': mythic_essence,
        },
        'skins_info': {
            'owned_skins': owned_skins_res,
            'normal_skins': normal_skins,
            'permanent_skins': permanent_skins,
        },
        'honor_info': honor_level_res,
        'rank_info': rank_info_res,
    }
