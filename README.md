# league-client

league-client is a python package to communicate with riot servers

We are actively developing 2.x.x version of this package, if you need the documentation or code of old version, please refer [1.x.x](https://github.com/sandbox-pokhara/league-client/tree/1.x.x) branch.

## Installation

```
pip install -U league-client
```

## Usage

### RSO

```py
from league_client.constants import LEAGUE_CLIENT_AUTH_PARAMS
from league_client.constants import RIOT_CLIENT_AUTH_PARAMS
from league_client.rso.auth import InventoryTypes
from league_client.rso.auth import get_champion_inventory_token
from league_client.rso.auth import get_entitlements_token
from league_client.rso.auth import get_event_inventory_token
from league_client.rso.auth import get_inventory_token
from league_client.rso.auth import get_inventory_token_v2
from league_client.rso.auth import get_ledge_token
from league_client.rso.auth import get_login_queue_token
from league_client.rso.auth import login_using_credentials
from league_client.rso.auth import login_using_ssid
from league_client.rso.auth import process_access_token
from league_client.rso.constants import DISCOVEROUS_SERVICE_LOCATION
from league_client.rso.constants import LEAGUE_EDGE_URL
from league_client.rso.constants import PLAYER_PLATFORM_EDGE_URL
from league_client.rso.missions import get_missions
from league_client.rso.rank import get_ranked_overview_token
from league_client.rso.rank import get_ranked_stats
from league_client.rso.userinfo import get_userinfo

# use riot client auth for basic stuffs like
# riot id, account id, etc
params = RIOT_CLIENT_AUTH_PARAMS

# use league client auth params if you need to parse
# league client data like rank, match history, missions, loot, etc
params = LEAGUE_CLIENT_AUTH_PARAMS

# login using credentials
(
    ssid,
    access_token,
    scope,
    iss,
    id_token,
    token_type,
    session_state,
    expires_in,
) = login_using_credentials("USERNAME", "PASSWORD", params)

# or login using session id, if you have already logged in once
# recommended to avoid rate limit
(
    ssid,
    access_token,
    scope,
    iss,
    id_token,
    token_type,
    session_state,
    expires_in,
) = login_using_ssid(ssid, params)


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
# inventory tokens, v1 & v2
# set inventory_types to List[InventoryTypes], as required
# required inventoryTypes can be found in function definition
# eg. get_party_data requires
# inventoryTypes = ["CHAMPION", "CHAMPION_SKIN", "SKIN_BORDER", "SKIN_AUGMENT"]
inventory_token = get_inventory_token(
    ledge_token,
    puuid,
    account_id,
    discoverous_service_location,
    league_edge_url,
    [InventoryTypes.champion, InventoryTypes.champion_skin],
)
inventory_token_v2 = get_inventory_token_v2(
    ledge_token,
    puuid,
    account_id,
    discoverous_service_location,
    league_edge_url,
    [InventoryTypes.queue_entry],
)
# inventoryTypes = ["EVENT_PASS"]
event_inventory_token = get_event_inventory_token(
    ledge_token,
    puuid,
    account_id,
    discoverous_service_location,
    league_edge_url,
)
# inventoryTypes = ["CHAMPION_SKIN"]
champion_inventory_token = get_champion_inventory_token(
    ledge_token,
    puuid,
    account_id,
    discoverous_service_location,
    league_edge_url,
)

# parse missions
missions = get_missions(
    ledge_token,
    league_edge_url,
    event_inventory_token,
    champion_inventory_token,
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
ranked_stats = get_ranked_stats(
    ledge_token,
    league_edge_url,
)
# ranked_stats =
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
    ranked_stats,
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
    inventory_token,    # champion, champion_skin, skin_border, skin_augment
    inventory_token_v2, # queue_entry
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
