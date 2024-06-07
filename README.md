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

# login using credentials
auth = login_using_credentials("USERNAME", "PASSWORD")

# or login using session id, if you have already logged in once
# recommended to avoid rate limit
auth = login_using_ssid(auth.ssid)

# auth object has following attributes
# auth = Auth(ssid='ey...', access_token='ey...', scope='openid link ban lol_region lol summoner offline_access', iss='https://auth.riotgames.com', id_token='ey...', token_type='Bearer', session_state='...', expires_in='3600')

# parse entitlement token
entitlements_token = get_entitlements_token(auth)

# parse pas token
pas_token = get_pas_token(auth)

# parse userinfo
userinfo = get_userinfo(auth)
# {'country': 'usa', 'sub': '...', 'lol_account': {'summoner_id': ..., 'profile_icon': ..., 'summoner_level': ..., 'summoner_name': ''}, 'email_verified': ..., 'player_plocale': ..., 'country_at': ..., 'pw': {'cng_at': ..., 'reset': ..., 'must_reset': ...}, 'lol': {'cuid': ..., 'cpid': '...', 'uid': ..., 'pid': '...', 'apid': ..., 'ploc': '...', 'lp': ..., 'active': ...}, 'original_platform_id': '...', 'original_account_id': ..., 'phone_number_verified': ..., 'photo': '...', 'preferred_username': '...', 'ban': {'restrictions': []}, 'ppid': ..., 'lol_region': [{'cuid': ..., 'cpid': '...', 'uid': ..., 'pid': '...', 'lp': ..., 'active': ...}], 'player_locale': '...', 'pvpnet_account_id': ..., 'region': {'locales': ..., 'id': '...', 'tag': '...'}, 'acct': {'type': ..., 'state': '...', 'adm': ..., 'game_name': '...', 'tag_line': '...', 'created_at': ...}, 'jti': '...', 'username': '...'}

# chat server information
get_chat_affinity_server(pas_token)  # jp1
get_chat_host(pas_token)  # jp1.chat.si.riotgames.com
```
