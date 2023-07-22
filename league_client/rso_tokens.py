import json
import re
from base64 import urlsafe_b64decode

import aiohttp

from league_client.exceptions import ParseError
from league_client.exceptions import RSOAuthorizeError
from league_client.rso_auth import parse_auth_code

from .logger import logger
from .rso_auth import rso_authorize


def _parse_access_token_regex(data):
    """Extract access token from data

    Args:
        data (dict): response json from authorization request

    Raises:
        ParseError

    Returns:
        str: parsed access token
    """

    try:
        pattern = re.compile(
            r"access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)"
        )
        token = pattern.findall(data["response"]["parameters"]["uri"])[0][0]
        return token
    except (re.error, KeyError, IndexError) as e:
        logger.exception("Failed to parse tokens (regex)")
        raise ParseError("Failed to parse tokens (regex)") from e


def parse_info_from_access_token(access_token):
    """Parse info from access token

    Args:
        access_token (str): access token

    Raises:
        ParseError

    Returns:
        dict:
            puuid (str): player uuid
            account_id (str): account id
            region (str): region
    """
    try:
        payload = access_token.split(".")[1]
        info = urlsafe_b64decode(f"{payload}===")
        data = json.loads(info)
        return {
            "puuid": data["sub"],
            "account_id": data["dat"]["u"],
            "region": data["dat"]["r"],
        }
    except (ValueError, KeyError, IndexError, TypeError) as e:
        logger.exception("Failed to parse info from access token")
        raise ParseError("Failed to parse info from access token") from e


async def parse_entitlements_token(session, access_token, proxy=None, proxy_auth=None):
    """Parse entitlements token using access token

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
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
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
                raise RSOAuthorizeError(
                    "Failed to get entitlements token", "ENTITLEMENTS_TOKEN"
                )
            return (await res.json())["entitlements_token"]
    except (aiohttp.ClientError, ValueError, KeyError) as e:
        logger.exception("Failed to parse entitlements token")
        raise ParseError("Failed to parse entitlements token", "UNKNOWN") from e


async def get_tokens(
    session,
    username,
    password,
    proxy=None,
    proxy_auth=None,
    client_id="lol",
    scope="openid offline_access lol ban profile email phone birthdate lol_region",
    entitlement=False,
):
    """Authorize RSO and get access token and entitlements token(optional)

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
    """
    access_token = entitlements_token = None
    await parse_auth_code(session, client_id, scope, proxy, proxy_auth)
    data = await rso_authorize(session, username, password, proxy, proxy_auth)
    access_token = _parse_access_token_regex(data)
    if entitlement:
        entitlements_token = await parse_entitlements_token(
            session, access_token, proxy, proxy_auth
        )
    return {"access_token": access_token, "entitlements_token": entitlements_token}
