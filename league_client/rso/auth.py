from enum import Enum
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import urlparse

import httpx
from httpx._types import ProxyTypes
from pydantic import BaseModel

from league_client.constants import AUTH_PARAMS
from league_client.constants import HEADERS
from league_client.constants import SSL_CONTEXT
from league_client.exceptions import AuthFailureError
from league_client.exceptions import InvalidSessionError


class Auth(BaseModel):
    ssid: str
    access_token: str
    scope: str
    iss: str
    id_token: str
    token_type: str
    session_state: str
    expires_in: str


class AuthLol(Auth):
    pass


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
    return {
        "access_token": qs["access_token"][0],
        "scope": qs["scope"][0],
        "iss": qs["iss"][0],
        "id_token": qs["id_token"][0],
        "token_type": qs["token_type"][0],
        "session_state": qs["session_state"][0],
        "expires_in": qs["expires_in"][0],
    }


def get_pas_token(auth: Auth, proxy: Optional[ProxyTypes] = None):
    h = HEADERS.copy()
    h["Authorization"] = f"{auth.token_type} {auth.access_token}"
    res = httpx.get(
        "https://riot-geo.pas.si.riotgames.com/pas/v1/service/chat",
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    return res.text


def get_entitlements_token(auth: Auth, proxy: Optional[ProxyTypes] = None):
    h = HEADERS.copy()
    h["Authorization"] = f"{auth.token_type} {auth.access_token}"
    res = httpx.post(
        "https://entitlements.auth.riotgames.com/api/token/v1",
        headers=h,
        proxy=proxy,
        json={"urn": "urn:entitlement:%"},
    )
    res.raise_for_status()
    return res.json()["entitlements_token"]


def get_login_queue_token(
    auth_lol: AuthLol,
    userinfo_token: str,
    entitlements_token: str,
    region: str,
    player_platform_url: str,
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"{auth_lol.token_type} {auth_lol.access_token}"
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
    account_id: str,
    region: str,
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
    account_id: str,
    region: str,
    service_location: str,
    ledge_url: str,
    proxy: Optional[ProxyTypes] = None,
):
    return get_inventory_token(
        ledge_token,
        puuid,
        account_id,
        region,
        service_location,
        ledge_url,
        InventoryTypes.event_pass,
        proxy,
    )


def get_champion_inventory_token(
    ledge_token: str,
    puuid: str,
    account_id: str,
    region: str,
    service_location: str,
    ledge_url: str,
    proxy: Optional[ProxyTypes] = None,
):
    return get_inventory_token(
        ledge_token,
        puuid,
        account_id,
        region,
        service_location,
        ledge_url,
        InventoryTypes.champion_skin,
        proxy,
    )


def login_using_ssid(
    ssid: str,
    proxy: Optional[ProxyTypes] = None,
    auth_params: dict[str, str] = AUTH_PARAMS,
) -> Auth:
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
            return Auth(ssid=ssid, **data)
        raise InvalidSessionError(res.text, res.status_code)


def login_using_credentials(
    username: str, password: str, proxy: Optional[ProxyTypes] = None
):
    with httpx.Client(verify=SSL_CONTEXT, proxy=proxy) as client:
        res = client.post(
            "https://auth.riotgames.com/api/v1/authorization",
            params=AUTH_PARAMS,
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
            return Auth(ssid=ssid, **data)
        raise AuthFailureError(res.text, res.status_code)


def get_auth_lol(auth: Auth, proxy: Optional[ProxyTypes] = None) -> AuthLol:
    auth_params = AUTH_PARAMS.copy()
    auth_params["client_id"] = "lol"
    new_auth = login_using_ssid(
        auth.ssid, proxy=proxy, auth_params=auth_params
    )
    auth_lol = AuthLol(**new_auth.__dict__)
    return auth_lol
