from typing import Callable
from typing import Literal
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import urlparse

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS
from league_client.constants import RIOT_CLIENT_AUTH_PARAMS
from league_client.constants import SSL_CONTEXT
from league_client.exceptions import AuthFailureError
from league_client.exceptions import AuthMultifactorError
from league_client.exceptions import InvalidSessionError
from league_client.exceptions import RateLimitedError
from league_client.rso.utils import decode_token


def process_redirect_url(redirect_url: str):
    # redirect url is returned by
    # PUT https://auth.riotgames.com/api/v1/authorization
    #
    # the following data can be parsed from redirect url:
    # - access_token (aka rso_token)
    # - scope
    # - iss
    # - id_token
    # - token_type
    # - session_state
    # - expires_in
    url = urlparse(redirect_url)
    frag = url.fragment
    qs = parse_qs(frag)
    return (
        qs["access_token"][0],
        qs["scope"][0],
        qs["iss"][0],
        qs["id_token"][0],
        qs["token_type"][0],
        qs["session_state"][0],
        qs["expires_in"][0],
    )


def process_access_token(access_token: str) -> tuple[str, str, int]:
    data = decode_token(access_token)
    # puuid, region, account_id
    return data["sub"], data["dat"]["r"], data["dat"]["u"]


def get_pas_token(access_token: str, proxy: Optional[ProxyTypes] = None):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {access_token}"
    res = httpx.get(
        "https://riot-geo.pas.si.riotgames.com/pas/v1/service/chat",
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    return res.text


def get_entitlements_token(
    access_token: str, proxy: Optional[ProxyTypes] = None
) -> str:
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {access_token}"
    res = httpx.post(
        "https://entitlements.auth.riotgames.com/api/token/v1",
        headers=h,
        proxy=proxy,
        json={"urn": "urn:entitlement:%"},
    )
    res.raise_for_status()
    return res.json()["entitlements_token"]


def get_login_queue_token(
    access_token: str,
    userinfo_token: str,
    entitlements_token: str,
    region: str,
    player_platform_url: str,
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {access_token}"
    res = httpx.post(
        f"{player_platform_url}"
        f"/login-queue/v2/login/products/lol/regions/{region}",
        headers=h,
        json={
            "clientName": "lcu",
            "entitlements": entitlements_token,
            "userinfo": userinfo_token,
        },
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()["token"]


def get_ledge_token(
    login_queue_token: str,
    puuid: str,
    region: str,
    player_platform_url: str,
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {login_queue_token}"
    res = httpx.post(
        f"{player_platform_url}/session-external/v1/session/create",
        headers=h,
        json={
            "claims": {"cname": "lcu"},
            "product": "lol",
            "puuid": puuid,
            "region": region.lower(),
        },
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()


def get_summoner_token(
    ledge_token: str,
    puuid: str,
    region: str,
    ledge_url: str,
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {ledge_token}"
    res = httpx.get(
        f"{ledge_url}"
        f"/summoner-ledge/v1/regions/{region}/summoners/puuid/{puuid}/jwt",
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()


def login_using_ssid(
    ssid: str,
    clid: str,
    auth_params: dict[str, str] = RIOT_CLIENT_AUTH_PARAMS,
    proxy: Optional[ProxyTypes] = None,
) -> tuple[str, str, str, str, str, str, str, str, str]:
    with httpx.Client(verify=SSL_CONTEXT, proxy=proxy) as client:
        if ssid:
            client.cookies.set("ssid", ssid, domain="auth.riotgames.com")
            client.cookies.set("clid", clid, domain="auth.riotgames.com")
        res = client.post(
            "https://auth.riotgames.com/api/v1/authorization",
            params=auth_params,
            headers=HEADERS,
        )
        res.raise_for_status()
        data = res.json()
        if "response" in data:
            ssid = client.cookies["ssid"]
            redirect_url = data["response"]["parameters"]["uri"]
            data = process_redirect_url(redirect_url)
            return (ssid, clid, *data)
        raise InvalidSessionError(res.text, res.status_code)


def authorize(
    client: httpx.Client,
    username: str,
    password: str,
    captcha_solver: Callable[[str, str], str],
    params: dict[str, str] = RIOT_CLIENT_AUTH_PARAMS,
    type: Literal["auth", "re-auth"] = "auth",
):
    # the authorization flow is different for
    # website (prod-xsso-riotgames, accountodactyl-prod)
    # and client (riot-client, lol)
    #
    # this flow is based on website but works
    # for (riot-client, lol)
    #
    # if this flow stops working for (riot-client, lol)
    # revert to commit 5f1bbba

    # step 1: set authorization params
    url = "https://auth.riotgames.com/authorize"
    res = client.get(
        url, params=params, headers=HEADERS, follow_redirects=True
    )
    res.raise_for_status()

    # step 2: get hcaptcha details (sitekey and rqdata)
    url = "https://authenticate.riotgames.com/api/v1/login"
    res = client.get(url, headers=HEADERS)
    res.raise_for_status()
    data = res.json()
    site_key = data["captcha"]["hcaptcha"]["key"]
    site_data = data["captcha"]["hcaptcha"]["data"]

    # step 3: solve captcha
    token = captcha_solver(site_data, site_key)

    # step 4: put authentication data (username/password)
    # the response contains login token
    url = "https://authenticate.riotgames.com/api/v1/login"
    if type == "auth":
        body = {
            "language": "en_US",
            "remember": True,
            "riot_identity": {
                "captcha": f"hcaptcha {token}",
                "password": password,
                "username": username,
            },
            "type": "auth",
        }
    else:
        body = {
            "type": "re-auth",
            "remember": True,
            "language": "en_US",
            "riot_identity": {
                "password": password,
                "captcha": f"hcaptcha {token}",
            },
        }
    res = client.put(url, json=body, headers=HEADERS)
    res.raise_for_status()

    # step 5: post login token/redirect to complete authentication
    data = res.json()
    response_type = data["type"]
    if response_type == "success":
        # riot-client and lol redirects to localhost
        # so, we use a different method to post login token
        # for these clients
        if params["client_id"] in ["riot-client", "lol"]:
            body = {
                "authentication_type": "RiotAuth",
                "code_verifier": "",
                "login_token": data["success"]["login_token"],
                "persist_login": True,
            }
            res = client.post(
                "https://auth.riotgames.com/api/v1/login-token",
                json=body,
                headers=HEADERS,
            )
            res.raise_for_status()
        else:
            # NOTE: not raising for status because it can raise false
            # positive when success
            client.get(
                data["success"]["redirect_url"],
                headers=HEADERS,
                follow_redirects=True,
            )
    elif response_type == "multifactor":
        raise AuthMultifactorError(res.text, res.status_code)
    elif response_type == "auth" and data["error"] == "auth_failure":
        raise AuthFailureError(res.text, res.status_code)
    elif response_type == "auth" and data["error"] == "rate_limited":
        raise RateLimitedError(res.text, res.status_code)
    else:
        raise AuthFailureError(res.text, res.status_code)


def login_using_credentials(
    username: str,
    password: str,
    captcha_solver: Callable[[str, str], str],
    params: dict[str, str] = RIOT_CLIENT_AUTH_PARAMS,
    proxy: Optional[ProxyTypes] = None,
) -> tuple[str, str, str, str, str, str, str, str, str]:
    with httpx.Client(verify=SSL_CONTEXT, proxy=proxy) as client:
        authorize(
            client,
            username,
            password,
            captcha_solver,
            params,
        )
        res = client.post(
            "https://auth.riotgames.com/api/v1/authorization",
            params=params,
            headers=HEADERS,
        )
        data = res.json()
        ssid = client.cookies["ssid"]
        clid = client.cookies["clid"]
        if "response" not in data:
            raise AuthFailureError(res.text, res.status_code)
        redirect_url = data["response"]["parameters"]["uri"]
        data = process_redirect_url(redirect_url)
        return (ssid, clid, *data)
