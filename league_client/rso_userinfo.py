from copy import copy

import aiohttp

from league_client.exceptions import ParseError
from league_client.exceptions import RSOAuthorizeError
from league_client.exceptions import SummonerNotFoundError
from league_client.rso import HEADERS
from league_client.rso import get_basic_auth
from league_client.utils import get_internal_region_by_platform
from league_client.utils import get_internal_region_by_tag

from .logger import logger


async def parse_userinfo(
    session, access_token, proxy=None, proxy_auth=None, parse_token=False
):
    """Get userinfo from RSO

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
                        'internal_region': (str) internal region
                        'game_name': (str) game name
            'token': (str or None) token (if parse_token=True)
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    info_res = token_res = None
    try:
        async with session.post(
            "https://auth.riotgames.com/userinfo",
            proxy=proxy,
            proxy_auth=proxy_auth,
            json={},
            headers=headers,
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise RSOAuthorizeError("Failed to get userinfo", "USERINFO")
            if not parse_token:
                userinfo = await res.json()
                if userinfo["lol_account"] is None:
                    internal_region = userinfo["original_platform_id"]
                    internal_region = get_internal_region_by_platform(internal_region)
                    raise SummonerNotFoundError(
                        "The account does not have a summoner",
                        "NO_SUMMONER",
                        internal_region,
                    )
                internal_region = get_internal_region_by_tag(userinfo["region"]["tag"])
                info_res = {
                    "country": userinfo["country"],
                    "sub": userinfo["sub"],
                    "summoner_name": userinfo["lol_account"]["summoner_name"],
                    "summoner_id": userinfo["lol_account"]["summoner_id"],
                    "summoner_level": userinfo["lol_account"]["summoner_level"],
                    "password_changed_at": userinfo["pw"]["cng_at"],
                    "email_verified": userinfo["email_verified"],
                    "phone_number_verified": userinfo["phone_number_verified"],
                    "username": userinfo["username"],
                    "ban_stats": userinfo["ban"],
                    "region": userinfo["region"]["tag"],
                    "internal_region": internal_region,
                    "game_name": userinfo["acct"]["game_name"],
                }
            else:
                token_res = await res.text()
            return {"info": info_res, "token": token_res}
    except (aiohttp.ClientError, ValueError, KeyError, TypeError) as e:
        logger.exception("Failed to parse userinfo")
        raise ParseError("Failed to parse userinfo", "UNKNOWN") from e


async def parse_accountinfo(
    session, csrf_token, proxy=None, proxy_user=None, proxy_pass=None
):
    """Get account info from Riot website

    Returns:
        {'sub': 'ffffffff-5555-5555-bbbb-999999999999',
        'email': 'Exa*******@gm***.com',
        'region': 'EUW1', 'locale': 'en',
        'username': 'Te******er', 'mfa': {'verified': True},
        'country': 'usa', 'email_status': 'not_validated',
        'federated_identities': ['xbox'],
        'birth_date': '2000-**-**'}
    """
    headers = copy(HEADERS)
    headers["csrf-token"] = csrf_token
    headers["referer"] = "https://account.riotgames.com/"
    async with session.get(
        "https://account.riotgames.com/api/account/v1/user",
        proxy=proxy,
        proxy_auth=get_basic_auth(proxy_user, proxy_pass),
        json={},
        headers=headers,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            logger.debug(await res.text())
            return None
        return await res.json()
