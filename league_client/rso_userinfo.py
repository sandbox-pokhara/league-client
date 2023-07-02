import aiohttp

from league_client.exceptions import ParseError
from league_client.exceptions import RSOAuthorizeError

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
                    "game_name": userinfo["acct"]["game_name"],
                }
            else:
                token_res = await res.text()
            return {"info": info_res, "token": token_res}
    except (aiohttp.ClientError, ValueError, KeyError, TypeError) as e:
        logger.exception("Failed to parse userinfo")
        raise ParseError("Failed to parse userinfo", "UNKNOWN") from e
