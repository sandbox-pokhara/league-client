# league-client

league-client is a python package to communicate with riot client, league client (LCU) and riot servers directly (RSO).

## Requirements

- Python 3.6+

## Installation

```
pip install league-client
```

## Known Limitations

- RSO does not work in python3.6

## Usage

### League Client

#### Authentication

```py
from league_client.shortcuts import login

riot_exe = 'C:\\Riot Games\\Riot Client\\RiotClientServices.exe'
riot_lockfile = 'C:\\Users\\sandbox\\AppData\\Local\\Riot Games\\Riot Client\\Config\\lockfile'
league_lockfile = 'C:\\Riot Games\\League of Legends\\lockfile'

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

If your account is already logged in you can simply do

```py
from league_connection import LeagueConnection

riot_lockfile = 'C:\\Users\\sandbox\\AppData\\Local\\Riot Games\\Riot Client\\Config\\lockfile'
league_lockfile = 'C:\\Riot Games\\League of Legends\\lockfile'

connection = LeagueConnection(league_lockfile)
riot_connection = LeagueConnection(riot_lockfile)
```

#### get_userinfo

```py
from league_client.riot import get_userinfo

get_userinfo(riot_connection)
# {'acct': {'game_name': 'callbackCat', 'tag_line': '6584'}, 'country': 'npl', 'email_verified': False, 'lol': {'cpid': 'SG2', 'ploc': 'en-US'}, 'lol_account': {'summoner_name': 'chaddiman'}, 'phone_number_verified': False, 'player_plocale': None, 'preferred_username': ''}
```

#### disenchant

```py
from league_client.disenchant import disenchant
disenchant(connection, loot)

from league_client.disenchant import disenchant_eternals
disenchant_eternals(connection)

from league_client.disenchant import disenchant_ward_skins
disenchant_ward_skins(connection)
```

### forge

```py
from league_client.forge import open_generic_chests
data = open_generic_chests(connection, repeat=5)
# 03/17/2024 07:02:14 PM - INFO - Forging CHEST_generic_OPEN, repeat: 5
# None

from league_client.forge import open_masterwork_chests
data = open_masterwork_chests(connection, repeat=1)
# 03/17/2024 07:03:26 PM - INFO - Forging CHEST_224_OPEN, repeat: 1
# None

from league_client.forge import open_champion_mastery_chest
data = open_champion_mastery_chest(connection, repeat=1)
# 03/17/2024 07:05:22 PM - INFO - Forging CHEST_champion_mastery_OPEN, repeat: 1
# None

from league_client.forge import forge_key_from_key_fragments
data = forge_key_from_key_fragments(connection, repeat=1)
# 03/17/2024 07:08:44 PM - INFO - Forging MATERIAL_key_fragment_forge, repeat: 1
# None

from league_client.forge import forge_keys_and_open_generic_chests
data = forge_keys_and_open_generic_chests(connection, retry_limit=10)
# None

from league_client.forge import forge_keys_and_open_masterwork_chests 
data = forge_keys_and_open_masterwork_chests(connection, retry_limit=10)
# None

from league_client.forge import open_orbs 
data = open_orbs(connection, retry_limit=10)
# None

from league_client.forge import open_bags
data = open_bags(connection, retry_limit=10)
# None

from league_client.forge import open_eternals_capsules 
data =  open_eternals_capsules(connection, retry_limit=10)
# None
```

#### friend_requests

```py
from league_client.friend_requests import get_friend_requests
get_friend_requests(connection)

from league_client.friend_requests import post_friend_requests
post_friend_requests(connection, summoner_puuid)
```

#### friends

```py
from league_client.friends import get_friend_exists
get_friend_exists(connection, summoner_id)
```

#### gifting

```py
from league_client.gifting import get_giftable_friends
get_giftable_friends(connection)

from league_client.gifting import post_gift
data = post_gift(
    token,
    sender_account_id,
    recipient,
    message,
    category_id,
    inventory_type,
    item_id,
    rp,
    quantity=1,
)
```

#### inventory

```py
from league_client.inventory import get_inventory_by_type
get_inventory_by_type(connection, inventory_type)

from league_client.inventory import get_owned_skins
get_owned_skins(connection, True)
```

#### loot

```py
from league_client.loot import get_loot
get_loot(connection)

from league_client.loot import get_player_loot_map
get_player_loot_map(connection)

from league_client.loot import get_loot_count
get_loot_count(connection)

from league_client.loot import get_loot_by_id
get_loot_by_id(connection, loot_id)

from league_client.loot import get_loot_by_pattern
get_loot_by_pattern(connection, pattern)

from league_client.loot import get_eternals
get_eternals(connection)

from league_client.loot import get_ward_skins
get_ward_skins(connection)

from league_client.loot import get_orange_essence
get_orange_essence(connection)

from league_client.loot import get_skin_shards
get_skin_shards(connection)

from league_client.loot import get_perma_skin_shards
get_perma_skin_shards(connection)

from league_client.loot import get_key_fragment_count
get_key_fragment_count(connection)

from league_client.loot import get_key_count
get_key_count(connection)

from league_client.loot import get_generic_chest_count
get_generic_chest_count(connection)

from league_client.loot import get_champion_mastery_chest_count
get_champion_mastery_chest_count(connection)

from league_client.loot import get_masterwork_chest_count
get_masterwork_chest_count(connection)

from league_client.loot import get_blue_essence_count
get_blue_essence_count(connection)
```

#### match_history

```py
from league_client.match_history import get_match_history
get_match_history(connection, puuid)
```

#### ranked

```py
from league_client.ranked import get_ranked_stats
get_ranked_stats(connection, puuid)
```

#### riot

```py
from league_client.riot import get_region
get_region(riot_connection)
```

#### summoner

```py
from league_client.summoner import get_summoner_by_name
get_summoner_by_name(connection, name)

from league_client.summoner import get_current_summoner
get_current_summoner(connection)

from league_client.summoner import get_summoner_level
get_summoner_level(connection)

from league_client.summoner import get_summoner_puuid
get_summoner_puuid(connection)

from league_client.summoner import get_summoner_id
get_summoner_id(connection)
```

#### username

```py
from league_client.username import get_username
get_username(connection)
```

#### wallet

```py
from league_client.wallet import get_wallet
get_wallet(connection)
```

### RSO

#### password

```py
from league_client.password import change_password
change_password(
    "username",
    "password",
    "new_password",
    proxy=None,
    proxy_user=None,
    proxy_pass=None,

)

from league_client.password import check_password
check_password(
    "username",
    "password",
    proxy=None,
    proxy_user=None,
    proxy_pass=None,

)

from league_client.password import send_verify_link
send_verify_link(
    "username",
    "password",
    "email@mail.com",
    proxy=None,
    proxy_user=None,
    proxy_pass=None,
)
```

#### riot_userinfo

```py
from league_client.password import get_riot_userinfo
get_riot_userinfo(
    "username",
    "password",
    proxy=None,
    proxy_user=None,
    proxy_pass=None,
)
```

#### account_info

```py
from league_client.rso_userinfo import parse_accountinfo
from league_client.rso import ClientSession

async def accountinfo():
    async with ClientSession() as session:
        csrf_token = await get_csrf_token(
            session, proxy=None, proxy_user=None, proxy_auth=None
        )
        await parse_accountinfo(
            session,
            csrf_token,
            proxy=None,
            proxy_auth=None,
            parse_pass=None,
        )
```


#### parse_ledge_token

```py
from league_client.rso_ledge import parse_ledge_token
from league_client.rso import ClientSession

async def ledge_token():
    async with ClientSession() as session:
        csrf_token = await get_csrf_token(
            session, proxy=None, proxy_user=None, proxy_auth=None
        )
        await parse_ledge_token(
            session,
            csrf_token,
            proxy=None,
            proxy_auth=None,
            parse_pass=None,
        )
```

#### rso_ledge

```py
from league_client.rso_ledge import get_owned_skins
from league_client.rso import ClientSession
from league_client.rso_ledge import get_honor_level
from league_client.rso_ledge import get_rank_info

async def rso_ledge():
    async with ClientSession() as session:
        owned_skins = await get_owned_skins(
            session,
            account_info,
            ledge_token,
            proxy=None,
            proxy_auth=None,
        )


        honor_level= await get_honor_level(
            session,
            account_info,
            ledge_token,
            proxy=None,
            proxy_auth=None,
        )

        rank_info = await get_rank_info(
            session,
            account_info,
            ledge_token,
            proxy=None,
            proxy_auth=None,
        )
```

#### rso_userinfo

```py
from league_client.rso import ClientSession
from league_client.rso_userinfo import parse_userinfo

async def userinfo():
    async with ClientSession() as session:
        await parse_userinfo(
            session,
            access_token,
            proxy=None,
            proxy_auth=None,
            parse_token=False,
        )
```

#### parse_blue_essence

```py
from league_client.rso import ClientSession
from league_client.utils import parse_blue_essence
from league_client.rso import HEADERS

async def userinfo():
    async with ClientSession() as session:
        await parse_blue_essence(
            session,
            region,
            headers=HEADERS,
            proxy=None,
            proxy_auth=None,
        )
```

#### parse_flash_key

```py
from league_client.utils import parse_flash_key
parse_flash_key(
    match_data,
    summoner_id
)
```
