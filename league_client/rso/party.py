from typing import Any
from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS


def get_party_data(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    account_id: int,
    region: str,
    id_token: str,
    entitlement_token: str,
    userinfo_token: str,
    summoner_token: str,
    ranked_overview_token: str,
    inventory_token: str,  # champion, champion_skin, skin_border, skin_augment
    inventory_token_v2: str,  # queue_entry
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {ledge_token}"
    res = httpx.put(
        f"{ledge_url}/parties-ledge/v1/players/{puuid}",
        headers=h,
        proxy=proxy,
        json={
            "accountId": account_id,
            "createdAt": 0,
            "currentParty": None,
            "eligibilityHash": 0,
            "parties": None,
            "platformId": region,
            "puuid": puuid,
            "registration": {
                "experiments": {},
                # https://sieve.services.riotcdn.net/api/v1/products/lol/version-sets/EUW1
                "gameClientVersion": "14.13.5989749+branch.releases-14-13.code.public.content.release.anticheat.vanguard",
                "inventoryToken": None,
                "inventoryTokens": [
                    inventory_token_v2,
                ],
                "playerTokens": {
                    "entitlementsToken": entitlement_token,
                    "idToken": id_token,
                    "summonerToken": summoner_token,
                    "userInfoToken": userinfo_token,
                },
                "rankedOverviewToken": ranked_overview_token,
                "simpleInventoryToken": inventory_token,
                "summonerToken": None,
            },
            "serverUtcMillis": 0,
            "summonerId": account_id,
            "tftGamesPlayed": 0,
            "tftGamesWon": 0,
            "version": 0,
        },
    )
    res.raise_for_status()
    return res.json()


def get_party_id(
    party_data: dict[str, Any],
) -> str:
    return party_data["currentParty"]["partyId"]


def get_party_restrictions(
    ledge_token: str,
    ledge_url: str,
    party_id: str,
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {ledge_token}"
    res = httpx.get(
        f"{ledge_url}/parties-ledge/v1/parties/{party_id}/restrictions",
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()
