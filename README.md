# league-client

league-client is a python package to communicate with riot servers

We are actively developing 2.x.x version of this package, if you need the documentation or code of old version, please refer [1.x.x](https://github.com/sandbox-pokhara/league-client/tree/1.x.x) branch.

## Installation

```
pip install -U league-client ucaptcha
```

## Usage

### RSO

```py
from ucaptcha import solve_captcha

from league_client.constants import LEAGUE_CLIENT_AUTH_PARAMS
from league_client.constants import RIOT_CLIENT_AUTH_PARAMS
from league_client.rso.auth import get_entitlements_token
from league_client.rso.auth import get_ledge_token
from league_client.rso.auth import get_login_queue_token
from league_client.rso.auth import get_summoner_token
from league_client.rso.auth import login_using_credentials
from league_client.rso.auth import login_using_ssid
from league_client.rso.auth import process_access_token
from league_client.rso.constants import DISCOVEROUS_SERVICE_LOCATION
from league_client.rso.constants import LEAGUE_EDGE_URL
from league_client.rso.constants import PLAYER_PLATFORM_EDGE_URL
from league_client.rso.constants import InventoryTypes
from league_client.rso.inventory import get_inventory_data
from league_client.rso.inventory import get_inventory_data_v2
from league_client.rso.inventory import get_inventory_token
from league_client.rso.inventory import get_inventory_token_v2
from league_client.rso.missions import get_missions
from league_client.rso.party import get_party_data
from league_client.rso.party import get_party_id
from league_client.rso.party import get_party_restrictions
from league_client.rso.rank import get_rank_data
from league_client.rso.rank import get_ranked_overview_token
from league_client.rso.userinfo import get_userinfo

# captcha_solver is a function that takes rqdata and sitekey as arguments
# and should return a token, ucaptcha is used here, but you can use your
# custom code here
def captcha_solver(rqdata: str, sitekey: str) -> str:
    return solve_captcha(
        "twocaptcha", # other captcha service might not work
        "...",
        sitekey,
        "https://authenticate.riotgames.com/",
        rqdata=rqdata,
        enterprise=True,
        invisible=True,
    )

# use riot client auth for basic stuffs like
# riot id, account id, etc
params = RIOT_CLIENT_AUTH_PARAMS

# use league client auth params if you need to parse
# league client data like rank, match history, missions, loot, etc
params = LEAGUE_CLIENT_AUTH_PARAMS


# login using credentials
(
    ssid,
    clid,
    access_token,
    scope,
    iss,
    id_token,
    token_type,
    session_state,
    expires_in,
) = login_using_credentials(
    "username",
    "password",
    captcha_solver,
    params=RIOT_CLIENT_AUTH_PARAMS,
    proxy="proxy",
)
# or login using session id, if you have already logged in once
# recommended to avoid rate limit
(
    ssid,
    clid,
    access_token,
    scope,
    iss,
    id_token,
    token_type,
    session_state,
    expires_in,
) = login_using_ssid(ssid, clid, params)


# puuid, region and account_id can be parsed from access_token
puuid, region, account_id = process_access_token(access_token)

# use region to find
# - player_platform_edge_url
# - discoverous_service_location
# - league_edge_url
player_platform_edge_url = PLAYER_PLATFORM_EDGE_URL[region]
discoverous_service_location = DISCOVEROUS_SERVICE_LOCATION[region]
league_edge_url = LEAGUE_EDGE_URL[region]

# parse userinfo from access_token,
# returns json if riot client params is used
# returns jwt token if league client params is used
userinfo = get_userinfo(access_token)
# {'country': 'usa', 'sub': '...', 'lol_account': {'summoner_id': ..., 'profile_icon': ..., 'summoner_level': ..., 'summoner_name': ''}, 'email_verified': ..., 'player_plocale': ..., 'country_at': ..., 'pw': {'cng_at': ..., 'reset': ..., 'must_reset': ...}, 'lol': {'cuid': ..., 'cpid': '...', 'uid': ..., 'pid': '...', 'apid': ..., 'ploc': '...', 'lp': ..., 'active': ...}, 'original_platform_id': '...', 'original_account_id': ..., 'phone_number_verified': ..., 'photo': '...', 'preferred_username': '...', 'ban': {'restrictions': []}, 'ppid': ..., 'lol_region': [{'cuid': ..., 'cpid': '...', 'uid': ..., 'pid': '...', 'lp': ..., 'active': ...}], 'player_locale': '...', 'pvpnet_account_id': ..., 'region': {'locales': ..., 'id': '...', 'tag': '...'}, 'acct': {'type': ..., 'state': '...', 'adm': ..., 'game_name': '...', 'tag_line': '...', 'created_at': ...}, 'jti': '...', 'username': '...'}

# parse tokens
entitlements_token = get_entitlements_token(access_token)
login_queue_token = get_login_queue_token(
    access_token,
    str(userinfo),
    entitlements_token,
    region,
    player_platform_edge_url,
)
ledge_token = get_ledge_token(
    login_queue_token,
    puuid,
    region,
    player_platform_edge_url,
)
summoner_token = get_summoner_token(
    ledge_token,
    puuid,
    region,
    league_edge_url,
)

# inventory data & tokens, v1 & v2
# set inventory_types to List[InventoryTypes], as required
# required inventoryTypes can be found in function definition
# eg. get_party_data requires
# inventoryTypes = ["CHAMPION", "CHAMPION_SKIN", "SKIN_BORDER", "SKIN_AUGMENT"]
inventory_data = get_inventory_data(
    ledge_token,
    puuid,
    account_id,
    discoverous_service_location,
    league_edge_url,
    [InventoryTypes.champion, InventoryTypes.champion_skin],
)
inventory_token = get_inventory_token(inventory_data)
inventory_data_v2 = get_inventory_data_v2(
    ledge_token,
    puuid,
    account_id,
    discoverous_service_location,
    league_edge_url,
    [InventoryTypes.queue_entry],
)
inventory_token_v2 = get_inventory_token_v2(inventory_data_v2)
# inventory_data_v1/v2 =
# {
#   "sub: "...",
#   "items": {
#       "InventoryTypes.champion": [...],
#       "InventoryTypes.skin_border": [...],
#       ...
#    }
#    ...
# }
# examples:
# inventoryTypes = ["EVENT_PASS"]
event_pass_inventory_token = get_inventory_token(
    get_inventory_data(
        ledge_token,
        puuid,
        account_id,
        discoverous_service_location,
        league_edge_url,
        inventory_types=[
            InventoryTypes.event_pass,
        ],
    )
)
# inventoryTypes = ["CHAMPION_SKIN"]
champion_skin_inventory_token = get_inventory_token(
    get_inventory_data(
        ledge_token,
        puuid,
        account_id,
        discoverous_service_location,
        league_edge_url,
        inventory_types=[
            InventoryTypes.champion_skin,
        ],
    )
)

# parse missions
missions = get_missions(
    ledge_token,
    league_edge_url,
    [event_pass_inventory_token, champion_skin_inventory_token],
    str(userinfo),
)
# missions =
# {
#   "playerMissions: [
#       {
#         "title": ...,
#         "status": ...,
#         ...
#       }
#    ],
#   "playerSeries": [
#       {
#         "title": ...,
#         "status": ...,
#         ...
#       }
#    ],
# }

# parse rank data
rank_data = get_rank_data(
    ledge_token,
    league_edge_url,
)
# rank_data =
# {
#   "queues: [
#       {
#         "queueType": "RANKED_SOLO_5x5",
#         "tier": "GOLD",
#         "rank": "II",
#         "wins": 11,
#         "losses": 2,
#         "highestTier": "GOLD",
#         "highestRank": "IV",
#         "previousSeasonHighestTier": "PLATINUM",
#         "previousSeasonHighestRank": "III",
#         ...
#       },
#       ...
#    ],
#   ...
# }
ranked_overview_token = get_ranked_overview_token(
    rank_data,
)

# parse party data
party_data = get_party_data(
    ledge_token,
    league_edge_url,
    puuid,
    account_id,
    region,
    id_token,
    entitlements_token,
    str(userinfo),
    summoner_token,
    ranked_overview_token,
    inventory_token,  # champion, champion_skin, skin_border, skin_augment
    inventory_token_v2,  # queue_entry
)
party_id = get_party_id(party_data)
party_restrictions = get_party_restrictions(
    ledge_token,
    league_edge_url,
    party_id,
)
# party_restrictions =
# {
#   "partyRestrictions: [
#       {
#         "accountId": ...,
#         "reason": "TFT_NEW_PLAYER_RESTRICTED",
#         "queueId": 1160
#         ...
#       }
#   ],
#   "availableQueueIds": [
#       450,
#       1090,
#       ...
#    ]
# }
# availableQueueIds reference:
# https://static.developer.riotgames.com/docs/lol/queues.json
# https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/queues.json
```

### Use Cases Summary

For parsing specific data, use preferred method from the following cases:

- Account Region

```
_, region, _ = process_access_token(access_token)
```

```
# params = RIOT_CLIENT_AUTH_PARAMS
get_userinfo(access_token)["dat"]["r"]
```

```
# params = LEAGUE_CLIENT_AUTH_PARAMS
decode_token(str(userinfo))["dat"]["r"]
```

```
decode_token(id_token)["lol_region"]["cpid"]
```

```
decode_token(id_token)["lol_region"]["pid"]
```

- Account Verified (Email, Phone)

```
get_is_email_verified(access_token)
get_is_phone_verified(access_token)
```

```
decode_token(id_token)["account_verified"]
decode_token(id_token)["phone_number_verified"]
```

```
# params = RIOT_CLIENT_AUTH_PARAMS
get_userinfo(access_token)["email_verified"]
get_userinfo(access_token)["phone_number_verified"]
```

```
# params = LEAGUE_CLIENT_AUTH_PARAMS
decode_token(str(userinfo))["email_verified"]
decode_token(str(userinfo))["phone_number_verified"]
```

- Federated Identities

(Returns a list of federated identity providers)

```
decode_token(login_queue_token)["federated_identity_providers"]
```

```
decode_token(ledge_token)["federated_identity_providers"]
```

- Account Level

```
# params = RIOT_CLIENT_AUTH_PARAMS
get_userinfo(access_token)["lol_account"]["summoner_level"]
```

```
# params = LEAGUE_CLIENT_AUTH_PARAMS
decode_token(str(userinfo))["lol_account"]["summoner_level"]
```

```
decode_token(summoner_token)["level"]
```

- Account Rank, Wins/Losses

```
# e.g. tier='GOLD', rank='II'
rank_data = get_rank_data(...)
# queues: list of dict items
queues = rank_data["queues"]
# item: dict item, with queueType = RANKED_SOLO_5x5, RANKED_TFT, ...
# item = get item from queues where item["queueType"] == "RANKED_SOLO_5x5"
tier = item["tier]
rank = item["rank]
wins = item["wins"]
losses = item["losses"]
```

```
rank_data = get_rank_data(...)
tier, division, wins, losses = get_tier_division_wins_losses(rank_data)
```

- Blue/Orange/Mythic Essence

```
loot_data = get_loot_data(...)
player_loot = loot_data["playerLoot"]
# item1 = get item from player_loot where item["lootName"] == "CURRENCY_champion"
# item2 = get item from player_loot where item["lootName"] == "CURRENCY_cosmetic"
# item3 = get item from player_loot where item["lootName"] == "CURRENCY_mythic"
blueEssence = item1.count
orangeEssence = item2.count
mythicEssence = item3.count
```

```
loot_data = get_loot_data(...)
get_blue_essence_count(loot_data)
get_orange_essence_count(loot_data)
get_mythic_essence_count(loot_data)
```

- Account Skins

Owned skins

```
# inventoryTypes = ["CHAMPION_SKIN"]
champion_skin_inventory_data = get_inventory_data(
    ...,
    inventory_types=[InventoryTypes.champion_skin],
)
owned_skins = champion_skin_inventory_data["items"]["CHAMPION_SKIN"]
```

Normal and Permanent Skins

```
loot_data = get_loot_data(...)
player_loot = loot_data["playerLoot"]
# item_normal = filter items from player_loot where item["lootName"] contains "CHAMPION_SKIN_RENTAL"
# item_perm = filter items from player_loot where item["lootName"] contains "CHAMPION_SKIN_" and not in item_normal
## parse skin id from lootname 'CHAMPION_SKIN_RENTAL_887011' -> 887011
# normal_skins = list of skin_ids from item_normal
# permanent_skins = list of skin_ids from item_perm
```

All Skins

```
owned_skins, normal_skins, permanent_skins = get_skins(
        champion_skin_inventory_data, loot_data
    )
```

- Account Honor Level

```
honor_data = get_honor_data(...)
honor_level = get_honor_level(honor_data)
```

- Account Match History, Flash Key

```
match_data = get_match_data(...)
# summoner_id = userinfo["lol_account"]["summoner_id"]
flash_key = get_flash_key(match_data, summoner_id)
```

- All Account Data

```
from shortcuts.rso import get_account_data

account_data = get_account_data(username, password, captcha_solver, proxy)
```
