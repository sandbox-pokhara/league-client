import aiohttp

from league_client.exceptions import ParseError
from league_client.exceptions import RSOAuthorizeError

from .logger import logger
from .rso import HEADERS
from .rso import get_basic_auth


# ! to deprecate, current_version='1.0.16', Use parse_auth_code instead
async def parsing_auth_code(
    session, params, proxy, proxy_user=None, proxy_pass=None
):
    async with session.get(
        "https://auth.riotgames.com/authorize",
        params=params,
        proxy=proxy,
        proxy_auth=get_basic_auth(proxy_user, proxy_pass),
        headers=HEADERS,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            return False
        return res.ok


async def rso_authorize(
    session, username, password, proxy=None, proxy_auth=None
):
    """Parse access token from authorization credentials

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
        dict:
        {
            "type": "response",
            "response": {
                "mode": "fragment",
                "parameters": {
                    "uri": (
                        "http://localhost/redirect#access_token=..."
                        "&scope=scope1+scope2"
                        "&iss=https://auth.riotgames.com"
                        "&id_token=..."
                        "&token_type=Bearer"
                        "&session_state=..."
                        "&expires_in=3600"
                    )
                },
            },
            "country": "npl",
        }
    """
    data = {
        "type": "auth",
        "username": username,
        "password": password,
        "remember": True,
    }
    try:
        async with session.put(
            "https://auth.riotgames.com/api/v1/authorization",
            proxy=proxy,
            proxy_auth=proxy_auth,
            json=data,
            headers=HEADERS,
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                raise RSOAuthorizeError(
                    "Failed to get access token", "ACCESS_TOKEN"
                )
            data = await res.json()
            response_type = data["type"]
            if response_type == "response":
                return data
            elif response_type == "multifactor":
                raise RSOAuthorizeError(
                    "Multifactor authentication", "MULTIFACTOR"
                )
            elif response_type == "auth" and data["error"] == "auth_failure":
                raise RSOAuthorizeError("Wrong password", "WRONG_PASSWORD")
            elif response_type == "auth" and data["error"] == "rate_limited":
                raise RSOAuthorizeError("Rate limited", "RATE_LIMITED")
            raise RSOAuthorizeError(
                f"Got response type: {response_type}", "UNKNOWN"
            )
    except (aiohttp.ClientError, ValueError, KeyError) as e:
        logger.exception("Failed to parse access token")
        raise ParseError("Failed to parse access token", "UNKNOWN") from e


async def parse_auth_code(
    session, client_id, scope, proxy=None, proxy_auth=None
):
    """Get auth permit from RSO

    Args:
        session (ClientSession): aiohttp session
        client_id (str): riot client id
        scope (_type_): rso request scope
        proxy (str, optional): proxy url. Defaults to None.
        proxy_auth (BasicAuth, optional): proxy auth(username, password). Defaults to None.

    Raises:
        RSOAuthorizeError: AUTH_CODE - Failed to get authorization code
        ParseError
    """
    data = {
        "acr_values": "",
        "claims": "",
        "client_id": client_id,
        "code_challenge": "",
        "code_challenge_method": "",
        "nonce": 1,
        "redirect_uri": "http://localhost/redirect",
        "response_type": "token id_token",
        "scope": scope,
    }
    try:
        async with session.post(
            "https://auth.riotgames.com/api/v1/authorization",
            params=data,
            proxy=proxy,
            proxy_auth=proxy_auth,
            headers=HEADERS,
        ) as res:
            if not res.ok:
                logger.debug(res.status)
                logger.debug(await res.text())
                raise RSOAuthorizeError(
                    "Failed to get authorization code", "AUTH_CODE"
                )
    except aiohttp.ClientError as e:
        logger.exception("Failed to parse authorization code")
        raise ParseError(
            "Failed to parse authorization code", "UNKNOWN"
        ) from e
