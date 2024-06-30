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
from league_client.rso.auth import get_entitlements_token
from league_client.rso.auth import get_pas_token
from league_client.rso.auth import login_using_credentials
from league_client.rso.auth import login_using_ssid
from league_client.rso.chat import get_chat_affinity_server
from league_client.rso.chat import get_chat_host
from league_client.rso.userinfo import get_userinfo

# auth for riot-client (basic account-data parsing)
# login using credentials
auth = login_using_credentials("USERNAME", "PASSWORD")

# or login using session id, if you have already logged in once
# recommended to avoid rate limit
auth = login_using_ssid(auth.ssid)

# auth object has following attributes
# auth = Auth(ssid='ey...', access_token='ey...', scope='openid link ban lol_region lol summoner offline_access', iss='https://auth.riotgames.com', id_token='ey...', token_type='Bearer', session_state='...', expires_in='3600')

# auth for lol (all LoL data parsing)
# auth_lol object is similar to auth,
# except for 'client_id' attribute during authorization
auth_lol = get_auth_lol(auth)

# parse entitlement token
entitlements_token = get_entitlements_token(auth)

# parse pas token
pas_token = get_pas_token(auth)

# parse userinfo_token
userinfo_token = get_userinfo_token(auth_lol)

# parse userinfo
userinfo = get_userinfo(auth)
# {'country': 'usa', 'sub': '...', 'lol_account': {'summoner_id': ..., 'profile_icon': ..., 'summoner_level': ..., 'summoner_name': ''}, 'email_verified': ..., 'player_plocale': ..., 'country_at': ..., 'pw': {'cng_at': ..., 'reset': ..., 'must_reset': ...}, 'lol': {'cuid': ..., 'cpid': '...', 'uid': ..., 'pid': '...', 'apid': ..., 'ploc': '...', 'lp': ..., 'active': ...}, 'original_platform_id': '...', 'original_account_id': ..., 'phone_number_verified': ..., 'photo': '...', 'preferred_username': '...', 'ban': {'restrictions': []}, 'ppid': ..., 'lol_region': [{'cuid': ..., 'cpid': '...', 'uid': ..., 'pid': '...', 'lp': ..., 'active': ...}], 'player_locale': '...', 'pvpnet_account_id': ..., 'region': {'locales': ..., 'id': '...', 'tag': '...'}, 'acct': {'type': ..., 'state': '...', 'adm': ..., 'game_name': '...', 'tag_line': '...', 'created_at': ...}, 'jti': '...', 'username': '...'}

# decode jwt token
decoded_accesstoken = decode_token(auth.access_token)

# get basic account-info
puuid = get_puuid(decoded_accesstoken)
region = get_region(decoded_accesstoken)
account_id = get_account_id(decoded_accesstoken)

# get urls
player_platform_url = get_player_platform_url(region)
ledge_url = get_ledge_url(region)

# get lol service location
service_location = get_service_location(region)

# get other tokens
login_q_token = get_login_queue_token(
    auth_lol, userinfo_token, entitlements_token, region, player_platform_url
)
ledge_token = get_ledge_token(
    login_q_token, puuid, region, player_platform_url
)
event_inventory_token = get_event_inventory_token(
    ledge_token, puuid, account_id, region, service_location, ledge_url
)
champion_inventory_token = get_champion_inventory_token(
    ledge_token, puuid, account_id, region, service_location, ledge_url
)

# get all missions
missions = get_missions(
    ledge_token,
    ledge_url,
    event_inventory_token,
    champion_inventory_token,
    userinfo_token,
)
# {
#   "playerMissions: {
#       "title": ...,
#       "status": ...,
#       ...
#    }
#   "playerSeries": {
#       "title": ...,
#       "status": ...,
#       ...
#    }
# }


# chat server information
get_chat_affinity_server(pas_token)  # jp1
get_chat_host(pas_token)  # jp1.chat.si.riotgames.com
```
