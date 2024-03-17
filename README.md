# league-client

league-client is a python package to communicate with riot client and league client.
This project contains LCU(League Client Ux APi) and RSO(Riot Sign On) API.

### RSO API (Riot Services Observatory API):

The RSO API, or Riot Services Observatory API, is a crucial component within the ecosystem of Riot Games, the developer behind popular titles such as League of Legends. This API serves as a conduit for accessing and managing data related to the performance, availability, and behavior of Riot's online services. It provides developers with insights into the health and status of various game services, including but not limited to authentication, matchmaking, game servers, and player data services.

### LCU API (League Client Update API):

The LCU API, or League Client Update API, is an essential component of the League of Legends ecosystem, designed to facilitate interaction with the League Client software. As League of Legends continually evolves with updates and new features, the LCU API provides developers with a means to programmatically interact with the client, enabling the creation of custom applications, tools, and integrations.

### RiotClientAPI:

The RiotClientAPI is a fundamental component of Riot Games' infrastructure, serving as the primary interface for interacting with the Riot Client software. As the gateway to Riot's ecosystem of games and services, the RiotClientAPI provides developers with a unified platform for accessing player data, managing game sessions, and integrating third-party applications.

## Requirements

- Python 3.6+

## Installation

```
pip install league-client
```

## Known Limitations

- RSO does not work in python3.6

## LCU API Examples

### Define paths

```py
from league_connection import LeagueConnection

riot_exe = 'C:\\Riot Games\\Riot Client\\RiotClientServices.exe'
riot_lockfile = 'C:\\Users\\sandbox\\AppData\\Local\\Riot Games\\Riot Client\\Config\\lockfile'
league_lockfile = 'C:\\Riot Games\\League of Legends\\lockfile'

connection = LeagueConnection(league_lockfile)
riot_connection = LeagueConnection(riot_lockfile)
```

### get_userinfo 

```py
from league_client.riot import get_userinfo

data = get_userinfo(riot_connection)
# {'acct': {'game_name': 'callbackCat', 'tag_line': '6584'}, 'country': 'npl', 'email_verified': False, 'lol': {'cpid': 'SG2', 'ploc': 'en-US'}, 'lol_account': {'summoner_name': 'chaddiman'}, 'phone_number_verified': False, 'player_plocale': None, 'preferred_username': ''}
```

### disenchant 

```py
from league_client.disenchant import disenchant
data = disenchant(connection, loot)

from league_client.disenchant import disenchant_eternals
data = disenchant_eternals(connection)

from league_client.disenchant import disenchant_ward_skins
data = disenchant_ward_skins(connection)
```

### forge

```py
from league_client.forge import open_generic_chests
data = open_generic_chests(connection, 5)
# 03/17/2024 07:02:14 PM - INFO - Forging CHEST_generic_OPEN, repeat: 5
# None

from league_client.forge import open_masterwork_chests
data = open_masterwork_chests(connection, 1)
# 03/17/2024 07:03:26 PM - INFO - Forging CHEST_224_OPEN, repeat: 1
# None

from league_client.forge import open_champion_mastery_chest
data = open_champion_mastery_chest(connection, 1)
# 03/17/2024 07:05:22 PM - INFO - Forging CHEST_champion_mastery_OPEN, repeat: 1
# None

from league_client.forge import forge_key_from_key_fragments
data = forge_key_from_key_fragments(connection, 1)
# 03/17/2024 07:08:44 PM - INFO - Forging MATERIAL_key_fragment_forge, repeat: 1
# None

from league_client.forge import forge_keys_and_open_generic_chests
data = forge_keys_and_open_generic_chests(connection, 10)
# None

from league_client.forge import forge_keys_and_open_masterwork_chests 
data = forge_keys_and_open_masterwork_chests(connection, 10)
# None

from league_client.forge import open_orbs 
data = open_orbs(connection, 10)
# None

from league_client.forge import open_bags
data = open_bags(connection, 10)
# None

from league_client.forge import open_eternals_capsules 
data =  open_eternals_capsules(connection, 10)
# None
```

### friend_requests

```py
from league_client.friend_requests import get_friend_requests
data = get_friend_requests(connection)

from league_client.friend_requests import post_friend_requests 
data = post_friend_requests(connection, summoner_puuid)
```

### friends

```py
from league_client.friends import get_friend_exists
data = get_friend_exists(connection, summoner_id)
```

### gifting

```py
from league_client.gifting import get_giftable_friends 
data = get_giftable_friends(connection)

from league_client.gifting import post_gift 
data = post_gift(connection)
```

### inventory

```py
from league_client.inventory import get_inventory_by_type
data = get_inventory_by_type(connection, inventory_type)

from league_client.inventory import get_owned_skins
data = get_owned_skins(connection, True)
```

### Authentication

```py
from league_client.shortcuts import login
login(
     'username',
     'password',
     riot_exe,
     riot_lockfile,
     league_lockfile,
     captcha_service,
     captcha_api_key,
)
# 05/10/2022 12:18:09 PM - INFO - Logging in...
# 05/10/2022 12:18:18 PM - INFO - Waiting for session...
# 05/10/2022 12:18:22 PM - INFO - Session state: IN_PROGRESS
# 05/10/2022 12:18:28 PM - INFO - Session state: SUCCEEDED
# 05/10/2022 12:18:28 PM - INFO - Checking username...
# {'ok': True}

from league_client.logout import logout
logout(league_lockfile)
```

### loot

```py
from league_client.loot import get_loot
data = get_loot(connection)

from league_client.loot import get_player_loot_map 
data = get_player_loot_map(connection)

from league_client.loot import get_loot_count 
data = get_loot_count(connection)

from league_client.loot import get_loot_by_id
data = get_loot_by_id(connection, loot_id)

from league_client.loot import get_loot_by_pattern
data = get_loot_by_pattern(connection, pattern)

from league_client.loot import get_eternals 
data = get_eternals(connection)

from league_client.loot import get_ward_skins 
data = get_ward_skins(connection)

from league_client.loot import get_orange_essence 
data = get_orange_essence(connection)

from league_client.loot import get_skin_shards 
data = get_skin_shards(connection)

from league_client.loot import get_perma_skin_shards 
data = get_perma_skin_shards(connection)

from league_client.loot import get_key_fragment_count 
data = get_key_fragment_count(connection)

from league_client.loot import get_key_count 
data = get_key_count(connection)

from league_client.loot import get_generic_chest_count 
data = get_generic_chest_count(connection)

from league_client.loot import get_champion_mastery_chest_count 
data = get_champion_mastery_chest_count(connection)

from league_client.loot import get_masterwork_chest_count 
data = get_masterwork_chest_count(connection)

from league_client.loot import get_blue_essence_count 
data = get_blue_essence_count(connection)
```

### match_history

```py
from league_client.match_history import get_match_history 
data = get_match_history(connection, puuid)
```

### ranked

```py
from league_client.ranked import get_ranked_stats
data = get_ranked_stats(connection, puuid)
```

### riot

```py
from league_client.riot import get_region
data = get_region(riot_connection)
```

### summoner

```py
from league_client.summoner import get_summoner_by_name
data = get_summoner_by_name(connection, name)

from league_client.summoner import get_current_summoner 
data = get_current_summoner(connection)

from league_client.summoner import get_summoner_level 
data = get_summoner_level(connection)

from league_client.summoner import get_summoner_puuid 
data = get_summoner_puuid(connection)

from league_client.summoner import get_summoner_id 
data = get_summoner_id(connection)
```

### username

```py
from league_client.username import get_username 
data = get_username(connection)
```

### wallet

```py
from league_client.wallet import get_wallet 
data = get_wallet(connection)
```

## RSO API Examples

### password

```py
from league_client.password import change_password 
data = change_password(
    "username",
    "password",
    "new_password",
    proxy=None,
    proxy_user=None,
    proxy_pass=None,

)

from league_client.password import check_password
data = check_password(
    "username",
    "password",
    proxy=None,
    proxy_user=None,
    proxy_pass=None,

)

from league_client.password import send_verify_link
data = send_verify_link(
    "username",
    "password",
    "email@mail.com",
    proxy=None,
    proxy_user=None,
    proxy_pass=None,
)
```

### riot_userinfo

```py
from league_client.password import get_riot_userinfo
data = get_riot_userinfo(
    "username",
    "password",
    proxy=None,
    proxy_user=None,
    proxy_pass=None,
) 
```

### rso_ledge 

```py
from league_client.rso_ledge import get_owned_skins 
data =  get_owned_skins(
    session,
    account_info,
    ledge_token,
    proxy=None,
    proxy_auth=None,
)


from league_client.rso_ledge import get_honor_level
data = get_honor_level(
    session,
    account_info,
    ledge_token,
    proxy=None,
    proxy_auth=None,
)

from league_client.rso_ledge import get_rank_info 
data = get_rank_info(
    session,
    account_info,
    ledge_token,
    proxy=None,
    proxy_auth=None,
)
```

### rso_userinfo

```py
from league_client.rso_userinfo import parse_userinfo
data = parse_userinfo(
    session,
    access_token,
    proxy=None,
    proxy_auth=None,
    parse_token=False,
)
```

### account_info

```py
from league_client.rso_userinfo import parse_accountinfo
data = parse_accountinfo(
    session,
    csrf_token,
    proxy=None,
    proxy_auth=None,
    parse_pass=None,
)
```

### parse_blue_essence

```py
from league_client.utils import parse_blue_essence
data = parse_blue_essence(
    session,
    region,
    headers,
    proxy=None,
    proxy_auth=None,
)
```

### parse_flash_key

```py
from league_client.utils import parse_flash_key
data = parse_flash_key(
    match_data,
    summoner_id
)
```

### Change Log

- Add option to pass custom user agent and cookies.
