from enum import Enum
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import urlparse

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS
from league_client.constants import RIOT_CLIENT_AUTH_PARAMS
from league_client.constants import SSL_CONTEXT
from league_client.exceptions import AuthFailureError
from league_client.exceptions import InvalidSessionError
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
):
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


class InventoryTypes(str, Enum):
    event_pass = "EVENT_PASS"
    champion_skin = "CHAMPION_SKIN"


def get_inventory_token(
    ledge_token: str,
    puuid: str,
    account_id: int,
    service_location: str,
    ledge_url: str,
    inventory_type: InventoryTypes,
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {ledge_token}"
    res = httpx.get(
        f"{ledge_url}/lolinventoryservice-ledge/v1/inventories/simple",
        headers=h,
        params={
            "puuid": puuid,
            "accountId": account_id,
            "location": service_location,
            "inventoryTypes": inventory_type,
        },
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()["data"]["itemsJwt"]


def get_event_inventory_token(
    ledge_token: str,
    puuid: str,
    account_id: int,
    service_location: str,
    ledge_url: str,
    proxy: Optional[ProxyTypes] = None,
):
    return get_inventory_token(
        ledge_token,
        puuid,
        account_id,
        service_location,
        ledge_url,
        InventoryTypes.event_pass,
        proxy,
    )


def get_champion_inventory_token(
    ledge_token: str,
    puuid: str,
    account_id: int,
    service_location: str,
    ledge_url: str,
    proxy: Optional[ProxyTypes] = None,
):
    return get_inventory_token(
        ledge_token,
        puuid,
        account_id,
        service_location,
        ledge_url,
        InventoryTypes.champion_skin,
        proxy,
    )


def login_using_ssid(
    ssid: str,
    auth_params: dict[str, str] = RIOT_CLIENT_AUTH_PARAMS,
    proxy: Optional[ProxyTypes] = None,
) -> tuple[str, str, str, str, str, str, str, str]:
    with httpx.Client(verify=SSL_CONTEXT, proxy=proxy) as client:
        if ssid:
            client.cookies.set("ssid", ssid, domain="auth.riotgames.com")
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
            return (ssid, *data)
        raise InvalidSessionError(res.text, res.status_code)


def login_using_credentials(
    username: str,
    password: str,
    params: dict[str, str] = RIOT_CLIENT_AUTH_PARAMS,
    proxy: Optional[ProxyTypes] = None,
) -> tuple[str, str, str, str, str, str, str, str]:
    with httpx.Client(verify=SSL_CONTEXT, proxy=proxy) as client:
        res = client.post(
            "https://auth.riotgames.com/api/v1/authorization",
            params=params,
            headers=HEADERS,
        )
        res.raise_for_status()
        data = {
            "type": "auth",
            "username": username,
            "password": password,
            "remember": True,
        }
        res = client.put(
            "https://auth.riotgames.com/api/v1/authorization",
            json=data,
            headers=HEADERS,
        )
        res.raise_for_status()
        data = res.json()
        if "response" in data:
            ssid = client.cookies["ssid"]
            redirect_url = data["response"]["parameters"]["uri"]
            data = process_redirect_url(redirect_url)
            return (ssid, *data)
        raise AuthFailureError(res.text, res.status_code)
