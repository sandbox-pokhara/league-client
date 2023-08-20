import asyncio

import aiohttp

from league_client.exceptions import AccountBannedError
from league_client.exceptions import AccountRestrictedError
from league_client.exceptions import ChatRestrictedError
from league_client.exceptions import ConnectedAccountsError
from league_client.exceptions import RiotUserInfoError
from league_client.exceptions import TimeBanError
from league_client.riot_userinfo import get_riot_userinfo
from league_client.rso import get_basic_auth
from league_client.rso_ledge import get_honor_level
from league_client.rso_ledge import get_loot
from league_client.rso_ledge import get_match_history
from league_client.rso_ledge import get_owned_skins
from league_client.rso_ledge import get_rank_info
from league_client.rso_ledge import parse_ledge_token
from league_client.rso_tokens import get_tokens
from league_client.rso_tokens import parse_info_from_access_token
from league_client.rso_userinfo import parse_userinfo
from league_client.utils import parse_flash_key


# use get_account_details() instead
async def get_account_info(
    username,
    password,
    skins=True,
    honor_level=True,
    rank_info=True,
    proxy=None,
    proxy_user=None,
    proxy_pass=None,
):
    """Get account info.

    Args:
        username (str): account username
        password (str): account password
        skins (bool, optional): whether to parse skins_info. Defaults to True.
        honor_level (bool, optional): whether to parse honor_info. Defaults to True.
        rank_info (bool, optional): whether to parse rank_info. Defaults to True.
        proxy (str, optional): proxy url. Defaults to None.
        proxy_user (str, optional): proxy username. Defaults to None.
        proxy_pass (str, optional): proxy password. Defaults to None.

    Returns:
        dict: 'user_info': {'summoner_level', 'summoner_name', 'email_verified', 'phone_number_verified', 'ban_stats', ...},
            'account_info': {'puuid', 'region', ...} or None,
            'essence_info': {'blue_essence', 'orange_essence', 'mythic_essence'} or None,
            'skins_info': {'owned_skins', 'normal_skins', 'permanent_skins'} or None,
            'honor_info': {'honor_level', ...} or None,
            'rank_info': {'rank', 'tier', 'wins', 'losses', ...} or None,
    """
    owned_skins_res = None
    loot_res = None
    honor_level_res = None
    rank_info_res = None
    tokens = None
    account_info = None
    normal_skins = None
    permanent_skins = None
    blue_essence = None
    orange_essence = None
    mythic_essence = None
    userinfo = {}
    proxy_auth = get_basic_auth(proxy_user, proxy_pass)
    async with aiohttp.ClientSession() as session:
        tokens = await get_tokens(
            session,
            username,
            password,
            proxy,
            proxy_auth,
            client_id="riot-client",
        )
        userinfo = await parse_userinfo(
            session,
            tokens["access_token"],
            proxy,
            proxy_auth,
            parse_token=False,
        )
    restrictions = userinfo["info"]["ban_stats"]["restrictions"]
    restrictions = [r["type"] for r in restrictions]
    # Check if account is banned or not
    if "PERMANENT_BAN" in restrictions:
        raise AccountBannedError("Account is banned.", code="ACCOUNT_BANNED")
    summoner_id = userinfo.get("info", {}).get("summoner_id", None)
    if (skins or honor_level or rank_info) and summoner_id:
        # if the account has some kind of restriction,
        # parse_ledge_token fails, therefore these exceptions must be rasied
        if restrictions != []:
            if "TEXT_CHAT_RESTRICTION" in restrictions:
                raise ChatRestrictedError(
                    "Account has chat restriction.", code="CHAT_RESTRICTED"
                )
            if "TIME_BAN" in restrictions:
                raise TimeBanError(
                    "Account has time ban restriction.", code="TIME_BAN"
                )
            raise AccountRestrictedError(
                "Account has one or more restrictions.",
                code="ACCOUNT_RESTRICTED",
            )
        async with aiohttp.ClientSession() as session:
            tokens = await get_tokens(
                session,
                username,
                password,
                proxy,
                proxy_auth,
                client_id="lol",
                entitlement=True,
            )
            account_info = parse_info_from_access_token(tokens["access_token"])
            account_info["summoner_id"] = summoner_id
            ledge_token = await parse_ledge_token(
                session, account_info, tokens, proxy, proxy_auth
            )
            if skins:
                owned_skins_res = await get_owned_skins(
                    session,
                    account_info,
                    ledge_token,
                    proxy=None,
                    proxy_auth=None,
                )
                loot_res = await get_loot(
                    session,
                    account_info,
                    ledge_token,
                    proxy=None,
                    proxy_auth=None,
                )
                blue_essence = loot_res["blue_essence"]
                orange_essence = loot_res["orange_essence"]
                mythic_essence = loot_res["mythic_essence"]
                normal_skins = loot_res["normal_skins"]
                permanent_skins = loot_res["permanent_skins"]
            if honor_level:
                honor_level_res = await get_honor_level(
                    session,
                    account_info,
                    ledge_token,
                    proxy=None,
                    proxy_auth=None,
                )
            if rank_info:
                rank_info_res = await get_rank_info(
                    session,
                    account_info,
                    ledge_token,
                    proxy=None,
                    proxy_auth=None,
                )
    return {
        "user_info": userinfo.get("info"),
        "account_info": account_info,
        "essence_info": {
            "blue_essence": blue_essence,
            "orange_essence": orange_essence,
            "mythic_essence": mythic_essence,
        },
        "skins_info": {
            "owned_skins": owned_skins_res,
            "normal_skins": normal_skins,
            "permanent_skins": permanent_skins,
        },
        "honor_info": honor_level_res,
        "rank_info": rank_info_res,
    }


async def fake_task(default=None):
    return default


async def get_account_details(
    username,
    password,
    skins=True,
    essence=True,
    rank=True,
    honor=True,
    match_history=True,
    flash_key=True,
    connected_accounts=True,
    proxy=None,
    proxy_user=None,
    proxy_pass=None,
):
    """
    Args:
        skins (bool, optional): get skins data. Defaults to True.
        essence (bool, optional): get essence data. Defaults to True.
        rank (bool, optional): get rank data. Defaults to True.
        honor (bool, optional): get honor data. Defaults to True.
        match_history (bool, optional): get match history. Defaults to True.
        flash_key (bool, optional): get flash key. Defaults to True.
        connected_accounts (bool, optional): if True, raises ConnectedAccountsError if account has connected accounts(Google, Xbox...)
                                        if False, ignores connected accounts. Only for accounts testing.
                                        Defaults to True as xbox can be used to login without password.

    Raises:
        AccountBannedError: permanent ban
        ChatRestrictedError
        TimeBanError
        AccountRestrictedError
        Base: LeagueClientError

    Returns:
        {
         'account_info': {'account_id': 7777722222200000,
                  'puuid': 'ffffffff-5555-5555-bbbb-999999999999',
                  'region': 'EUW1',
                  'summoner_id': 7777722222200000},
         'essence': {'blue_essence': 20000,
                     'mythic_essence': 10,
                     'orange_essence': 500},
         'flash_key': None,
         'honor_level': {'checkpoint': 0, 'honorLevel': 2, 'rewardsLocked': False},
         'rank': {'division': None,
                  'losses': 0,
                  'queue': 'RANKED_SOLO_5x5',
                  'tier': 'UNRANKED',
                  'wins': 0},
         'skins': {'normal_skins': [22007, 4005, 497018],
                   'owned_skins': [],
                   'permanent_skins': [58003]},
         'user_info': {'ban_stats': {'restrictions': []},
                       'country': 'usa',
                       'email_verified': False,
                       'game_name': 'name',
                       'internal_region': 'EUW',
                       'password_changed_at': 1644830696000,
                       'phone_number_verified': False,
                       'region': 'euw',
                       'sub': 'ffffffff-5555-5555-bbbb-999999999999',
                       'summoner_id': 7777722222200000,
                       'summoner_level': 32,
                       'summoner_name': 'name',
                       'username': 'uname'}
        }
    """
    return_data = {}
    proxy_auth = get_basic_auth(proxy_user, proxy_pass)
    async with aiohttp.ClientSession() as session:
        tokens = await get_tokens(
            session,
            username,
            password,
            proxy,
            proxy_auth,
            client_id="riot-client",
        )
        userinfo = await parse_userinfo(
            session,
            tokens["access_token"],
            proxy,
            proxy_auth,
            parse_token=False,
        )
        return_data["user_info"] = userinfo.get("info")
    restrictions = userinfo["info"]["ban_stats"]["restrictions"]
    restrictions = [r["type"] for r in restrictions]
    if "PERMANENT_BAN" in restrictions:
        raise AccountBannedError("Account is banned.", code="ACCOUNT_BANNED")
    if connected_accounts:
        acc_data = await get_riot_userinfo(
            username, password, proxy, proxy_user, proxy_pass
        )
        # early raise if riot userinfo cannot be fetched
        if acc_data is None:
            raise RiotUserInfoError(
                "Failed to get riot userinfo.", code="RIOT_USERINFO"
            )
        federated_identities = acc_data.get("federated_identities")
        if federated_identities:
            raise ConnectedAccountsError(
                f"{federated_identities}", code="CONNECTED_ACCOUNTS"
            )
    summoner_id = userinfo.get("info", {}).get("summoner_id", None)
    # if the account has some kind of restriction,
    # parse_ledge_token fails, therefore these exceptions must be rasied
    if restrictions != []:
        if "TEXT_CHAT_RESTRICTION" in restrictions:
            raise ChatRestrictedError(
                "Account has chat restriction.", code="CHAT_RESTRICTED"
            )
        if "TIME_BAN" in restrictions:
            raise TimeBanError(
                "Account has time ban restriction.", code="TIME_BAN"
            )
        raise AccountRestrictedError(
            "Account has one or more restrictions.",
            code="ACCOUNT_RESTRICTED",
        )
    async with aiohttp.ClientSession() as session:
        tokens = await get_tokens(
            session,
            username,
            password,
            proxy,
            proxy_auth,
            client_id="lol",
            entitlement=True,
        )
        account_info = parse_info_from_access_token(tokens["access_token"])
        account_info["summoner_id"] = summoner_id
        return_data["account_info"] = account_info
        if (
            ((skins or essence) and summoner_id)
            or rank
            or honor
            or match_history
            or flash_key
        ):
            ledge_token = await parse_ledge_token(
                session, account_info, tokens, proxy, proxy_auth
            )
            tasks = []
            tasks.append(
                get_owned_skins(
                    session,
                    account_info,
                    ledge_token,
                )
                if skins
                else fake_task()
            )
            tasks.append(
                get_loot(
                    session,
                    account_info,
                    ledge_token,
                )
                if essence or skins
                else fake_task()
            )
            tasks.append(
                get_honor_level(
                    session,
                    account_info,
                    ledge_token,
                )
                if honor
                else fake_task()
            )
            tasks.append(
                get_rank_info(
                    session,
                    account_info,
                    ledge_token,
                )
                if rank
                else fake_task()
            )
            tasks.append(
                get_match_history(
                    session,
                    tokens["access_token"],
                    account_info["region"],
                    account_info["puuid"],
                )
                if match_history or flash_key
                else fake_task()
            )
            (
                owned_skins_data,
                loot_data,
                honor_level_data,
                rank_data,
                match_history_data,
            ) = await asyncio.gather(*tasks)
            return_data["flash_key"] = parse_flash_key(
                match_history_data, summoner_id
            )
            return_data["match_history"] = (
                match_history_data if match_history else None
            )
            return_data["honor_level"] = honor_level_data
            return_data["rank"] = rank_data
            if skins:
                normal_skins_data = loot_data["normal_skins"]
                permanent_skins_data = loot_data["permanent_skins"]
                return_data["skins"] = {
                    "owned_skins": owned_skins_data,
                    "normal_skins": normal_skins_data,
                    "permanent_skins": permanent_skins_data,
                }
            if essence:
                blue_essence_data = loot_data["blue_essence"]
                orange_essence_data = loot_data["orange_essence"]
                mythic_essence_data = loot_data["mythic_essence"]
                return_data["essence"] = {
                    "blue_essence": blue_essence_data,
                    "orange_essence": orange_essence_data,
                    "mythic_essence": mythic_essence_data,
                }
    return return_data
