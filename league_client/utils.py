import re

from .logger import logger
from .rso import HEADERS


# ! deprecated_in='1.0.16', Use rso_tokens._parse_access_token_regex instead
def _extract_tokens(data: str) -> str:
    """Extract tokens from data"""

    pattern = re.compile(
        r"access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)"
    )
    response = pattern.findall(data["response"]["parameters"]["uri"])[0]
    return response


# ! deprecated_in='1.0.16', Use rso_tokens.parse_auth_access_token instead
async def parse_access_token(session, data, proxy, proxy_auth):
    async with session.put(
        "https://auth.riotgames.com/api/v1/authorization",
        proxy=proxy,
        proxy_auth=proxy_auth,
        json=data,
        headers=HEADERS,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            return {"error": "Failed to get access token"}, 1
        data = await res.json()
        response_type = data["type"]
        if response_type == "response":
            response = _extract_tokens(data)
            access_token = response[0]
            return {"access_token": access_token}, None
        elif response_type == "multifactor":
            return {"error": "Multifactor authentication"}, 1
        elif response_type == "auth" and data["error"] == "auth_failure":
            return {"error": "Wrong password"}, 1
        elif response_type == "auth" and data["error"] == "rate_limited":
            return {"error": "Rate limited"}, 1
        return {"error": "Got response type: {response_type}"}, 1


async def parse_blue_essence(session, region, headers, proxy, proxy_auth):
    async with session.get(
        f"https://{region}.store.leagueoflegends.com/storefront/v2/wallet?language=en_GB/",
        proxy=proxy,
        proxy_auth=proxy_auth,
        json={},
        headers=headers,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            return {"error": "Failed to parse blue essence"}, 1
        return await res.json(), None


def get_internal_region_by_tag(region):
    region_u = region.upper()
    if region_u == "LAN":
        return "LA1"
    elif region_u == "LAS":
        return "LA2"
    elif region_u == "OC":
        return "OC1"
    return region_u


def get_internal_region_by_platform(region):
    if region == "BR1":
        return "BR"
    if region == "EUN1":
        return "EUNE"
    if region == "EUW1":
        return "EUW"
    if region == "JP1":
        return "JP"
    if region == "KR":
        return "KR"
    if region == "LA1":
        return "LA1"
    if region == "LA2":
        return "LA2"
    if region == "NA1":
        return "NA"
    if region == "OC1":
        return "OC1"
    if region == "TR1":
        return "TR"
    if region == "RU":
        return "RU"
    if region == "PH2":
        return "PH2"
    if region == "SG2":
        return "SG2"
    if region == "TH2":
        return "TH2"
    if region == "TW2":
        return "TW2"
    if region == "VN2":
        return "VN2"
    return region


def parse_flash_key(match_data, summoner_id):
    """
    Returns: flash key ('D' or 'F') if found, else None
    """
    try:
        for players in match_data["games"][0]["json"]["participants"]:
            if players["summonerId"] == summoner_id:
                if players["spell1Id"] == 4:
                    return "D"
                elif players["spell2Id"] == 4:
                    return "F"
        return None
    except Exception:
        return None
