from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from typing import Any
from typing import Callable
from typing import Optional

from httpx._types import ProxyTypes

from league_client.constants import LEAGUE_CLIENT_AUTH_PARAMS
from league_client.constants import RIOT_CLIENT_AUTH_PARAMS
from league_client.exceptions import AccountCheckError
from league_client.exceptions import AuthFailureError
from league_client.rso.auth import get_entitlements_token
from league_client.rso.auth import get_ledge_token
from league_client.rso.auth import get_login_queue_token
from league_client.rso.auth import get_summoner_token
from league_client.rso.auth import login_using_credentials
from league_client.rso.auth import process_access_token
from league_client.rso.constants import DISCOVEROUS_SERVICE_LOCATION
from league_client.rso.constants import LEAGUE_EDGE_URL
from league_client.rso.constants import PLAYER_PLATFORM_EDGE_URL
from league_client.rso.constants import InventoryTypes
from league_client.rso.honor import get_honor_data
from league_client.rso.honor import get_honor_level
from league_client.rso.inventory import get_inventory_data
from league_client.rso.inventory import get_inventory_data_v2
from league_client.rso.inventory import get_inventory_token
from league_client.rso.inventory import get_inventory_token_v2
from league_client.rso.loot import get_blue_essence_count
from league_client.rso.loot import get_loot_data
from league_client.rso.loot import get_mythic_essence_count
from league_client.rso.loot import get_orange_essence_count
from league_client.rso.match import get_flash_key
from league_client.rso.match import get_match_data
from league_client.rso.party import get_party_data
from league_client.rso.party import get_party_id
from league_client.rso.party import get_party_restrictions
from league_client.rso.password import change_password_using_credentials
from league_client.rso.rank import get_rank_data
from league_client.rso.rank import get_ranked_overview_token
from league_client.rso.rank import get_tier_division_wins_losses
from league_client.rso.skin import get_skins
from league_client.rso.userinfo import get_userinfo
from league_client.rso.utils import decode_token


def get_internal_region_by_tag(region: str) -> str:
    reg_u = region.upper()
    mapping = {
        "LAN": "LA1",
        "LAS": "LA2",
        "OC": "OC1",
    }
    return mapping.get(reg_u, reg_u)


def get_account_data(
    username: str,
    password: str,
    captcha_solver: Callable[[str, str], str],
    proxy: Optional[ProxyTypes] = None,
):
    """
    Get account data using RSO.
    Takes ~20 seconds to complete.

    Returns:
    {
        "puuid":"085e5d68-84a0-5488-bde3-1234567890as",
        "country":"ita",
        "region":"EUW",
        "summoner_id":3538571892000000,
        "summoner_name":"",
        "level":30,
        "email_verified":False,
        "phone_verified":False,
        "flash_key":None,
        "tier":"UNRANKED",
        "division":None,
        "wins":0,
        "losses":0,
        "quickplay_wins":0,
        "quickplay_losses":0,
        "honor_level":2,
        "blue_essence":43015,
        "orange_essence":940,
        "mythic_essence":0,
        "owned_skins":[
            123
        ],
        "normal_skins":[
            117004,
            21002,
        ],
        "permanent_skins":[
            345
        ],
        "party_restrictions":[
                {
                    "accountId":...,
                    "reason":"GAME_BASED_RANK_RESTRICTED",
                    "queueId":420
                },
            ],
        "available_queues":[
            450,
            700
        ]
    }
    """
    # account_data: for storing final data to be returned
    account_data: dict[str, Any] = {}
    # dat: for storing intermediate data
    dat: dict[str, Any] = {}
    params = LEAGUE_CLIENT_AUTH_PARAMS
    (
        _,
        _,
        access_token,
        _,
        _,
        id_token,
        _,
        _,
        _,
    ) = login_using_credentials(
        username,
        password,
        captcha_solver,
        params,
        proxy=proxy,
    )

    with ThreadPoolExecutor(3) as executor:
        future_proessat = executor.submit(process_access_token, access_token)
        future_userinfo = executor.submit(get_userinfo, access_token, proxy)
        future_entitlements = executor.submit(
            get_entitlements_token, access_token, proxy
        )

        for future in as_completed(
            [future_proessat, future_userinfo, future_entitlements]
        ):
            if future is future_proessat:
                puuid, region, account_id = future.result()
                account_data["puuid"] = puuid
                dat["region"] = region
                dat["account_id"] = int(account_id)
                dat["ppedge_url"] = PLAYER_PLATFORM_EDGE_URL[region]
                dat["ledge_url"] = LEAGUE_EDGE_URL[region]
                dat["ds_location"] = DISCOVEROUS_SERVICE_LOCATION[region]

            elif future is future_userinfo:
                dat["userinfo_token"] = str(future.result())
                userinfo = decode_token(dat["userinfo_token"])
                restrictions = [
                    r["type"] for r in userinfo["ban"]["restrictions"]
                ]
                if restrictions:
                    if "PERMANENT_BAN" in restrictions:
                        raise AccountCheckError(
                            "Account is permanently banned."
                        )
                    if "TEXT_CHAT_RESTRICTION" in restrictions:
                        raise AccountCheckError(
                            "Account has chat restriction."
                        )
                    if "TIME_BAN" in restrictions:
                        raise AccountCheckError(
                            "Account has time ban restriction."
                        )
                    raise AccountCheckError("Account has game restrictions.")
                account_data["country"] = userinfo["country"]
                region_tag = userinfo["region"]["tag"]
                account_data["region"] = get_internal_region_by_tag(region_tag)
                account_data["summoner_id"] = userinfo["lol_account"][
                    "summoner_id"
                ]
                account_data["summoner_name"] = userinfo["lol_account"][
                    "summoner_name"
                ]
                account_data["level"] = userinfo["lol_account"][
                    "summoner_level"
                ]
                account_data["email_verified"] = userinfo["email_verified"]
                account_data["phone_verified"] = userinfo[
                    "phone_number_verified"
                ]

            elif future is future_entitlements:
                dat["entitlements_token"] = str(future.result())

    with ThreadPoolExecutor(2) as executor:
        future_loginq = executor.submit(
            get_login_queue_token,
            access_token,
            dat["userinfo_token"],
            dat["entitlements_token"],
            dat["region"],
            dat["ppedge_url"],
            proxy,
        )
        future_match = executor.submit(
            get_match_data,
            access_token,
            account_data["puuid"],
            dat["ppedge_url"],
            proxy,
            100,
        )

        for future in as_completed([future_loginq, future_match]):
            if future is future_loginq:
                login_queue_token = future.result()
                login_queue_data = decode_token(login_queue_token)
                if login_queue_data.get("federated_identity_providers"):
                    raise AccountCheckError(
                        "Account has third-party login providers"
                    )
                dat["ledge_token"] = get_ledge_token(
                    login_queue_token,
                    account_data["puuid"],
                    dat["region"],
                    dat["ppedge_url"],
                    proxy,
                )
                dat["summoner_token"] = get_summoner_token(
                    dat["ledge_token"],
                    account_data["puuid"],
                    dat["region"],
                    dat["ledge_url"],
                    proxy,
                )

            elif future is future_match:
                match_data = future.result()
                quickplay_wins = 0
                quickplay_losses = 0
                puuid = account_data["puuid"]

                for game in match_data["games"]:
                    if game["json"]["queueId"] == 490:
                        for participant in game["json"]["participants"]:
                            if participant["puuid"] == puuid:
                                if participant["win"]:
                                    quickplay_wins += 1
                                else:
                                    quickplay_losses += 1

                flash_key = get_flash_key(
                    match_data, account_data["summoner_id"]
                )
                account_data["flash_key"] = flash_key
                account_data["quickplay_wins"] = quickplay_wins
                account_data["quickplay_losses"] = quickplay_losses

    with ThreadPoolExecutor(6) as executor:
        future_loot = executor.submit(
            get_loot_data,
            dat["ledge_token"],
            dat["ledge_url"],
            account_data["puuid"],
            proxy,
        )
        future_rank = executor.submit(
            get_rank_data, dat["ledge_token"], dat["ledge_url"], proxy
        )
        future_honor = executor.submit(
            get_honor_data, dat["ledge_token"], dat["ledge_url"], proxy
        )
        future_skin_inventory = executor.submit(
            get_inventory_data,
            dat["ledge_token"],
            account_data["puuid"],
            dat["account_id"],
            dat["ds_location"],
            dat["ledge_url"],
            [InventoryTypes.champion_skin],
            proxy,
        )
        future_party_inventory1 = executor.submit(
            get_inventory_data,
            dat["ledge_token"],
            account_data["puuid"],
            dat["account_id"],
            dat["ds_location"],
            dat["ledge_url"],
            [
                InventoryTypes.champion,
                InventoryTypes.champion_skin,
                InventoryTypes.skin_border,
                InventoryTypes.skin_augment,
            ],
            proxy,
        )
        future_party_inventory2 = executor.submit(
            get_inventory_data_v2,
            dat["ledge_token"],
            account_data["puuid"],
            dat["account_id"],
            dat["ds_location"],
            dat["ledge_url"],
            [InventoryTypes.queue_entry],
            proxy,
        )

        for future in as_completed(
            [
                future_loot,
                future_rank,
                future_honor,
                future_skin_inventory,
                future_party_inventory1,
                future_party_inventory2,
            ]
        ):
            if future is future_loot:
                dat["loot_data"] = future.result()
                be = get_blue_essence_count(dat["loot_data"])
                oe = get_orange_essence_count(dat["loot_data"])
                me = get_mythic_essence_count(dat["loot_data"])
                account_data["blue_essence"] = be
                account_data["orange_essence"] = oe
                account_data["mythic_essence"] = me

            elif future is future_rank:
                rank_data = future.result()
                tier, division, wins, losses = get_tier_division_wins_losses(
                    rank_data
                )
                account_data["tier"] = tier
                account_data["division"] = division
                account_data["wins"] = wins
                account_data["losses"] = losses

                dat["ranked_overview_token"] = get_ranked_overview_token(
                    rank_data,
                )

            elif future is future_honor:
                honor_data = future.result()
                honor_level = get_honor_level(honor_data)
                account_data["honor_level"] = honor_level

            elif future is future_skin_inventory:
                dat["champion_skin_inventory_data"] = future.result()

            elif future is future_party_inventory1:
                dat["party_inventory_token1"] = get_inventory_token(
                    future.result()
                )

            elif future is future_party_inventory2:
                dat["party_inventory_token2"] = get_inventory_token_v2(
                    future.result()
                )

    owned_skins, normal_skins, permanent_skins = get_skins(
        dat["champion_skin_inventory_data"], dat["loot_data"]
    )
    account_data["owned_skins"] = owned_skins
    account_data["normal_skins"] = normal_skins
    account_data["permanent_skins"] = permanent_skins

    party_data = get_party_data(
        dat["ledge_token"],
        dat["ledge_url"],
        account_data["puuid"],
        dat["account_id"],
        dat["region"],
        id_token,
        dat["entitlements_token"],
        dat["userinfo_token"],
        dat["summoner_token"],
        dat["ranked_overview_token"],
        dat["party_inventory_token1"],
        dat["party_inventory_token2"],
    )
    party_id = get_party_id(party_data)
    party_restrictions = get_party_restrictions(
        dat["ledge_token"],
        dat["ledge_url"],
        party_id,
    )
    account_data["party_restrictions"] = party_restrictions[
        "partyRestrictions"
    ]
    #   {
    #     "accountId": ...,
    #     "reason": "GAME_BASED_RANK_RESTRICTED",
    #     "queueId": 420
    #     ...
    #   }
    # playable queue could be missing from available_queues
    # due to 'GAME_VERSION_NOT_SUPPORTED' restriction
    # so use party_restrictions instead of available_queues
    # check for restrictions: 'GAME_BASED_RANK_RESTRICTED' ...
    account_data["available_queues"] = party_restrictions["availableQueueIds"]

    return account_data


def check_password(
    username: str,
    password: str,
    captcha_solver: Callable[[str, str], str],
    proxy: Optional[ProxyTypes] = None,
) -> bool:
    try:
        login_using_credentials(
            username, password, captcha_solver, RIOT_CLIENT_AUTH_PARAMS, proxy
        )
        return True
    except AuthFailureError:
        return False


def change_password(
    username: str,
    password: str,
    captcha_solver: Callable[[str, str], str],
    new_password: str,
    proxy: Optional[ProxyTypes] = None,
) -> bool:
    return change_password_using_credentials(
        username, password, new_password, captcha_solver, proxy
    )
