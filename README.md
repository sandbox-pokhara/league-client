# league-client

league-client is a python package to communicate with riot client and league client.

## Installation

```
pip install league-client
```

## Examples

### Logging in (Riot Client)

```
from league_connection import LeagueConnection

from league_client.login import login
from league_process.process import open_league_client
from league_process.process import open_riot_client

DEFAULT_RIOT_EXE = 'C:\\Riot Games\\Riot Client\\RiotClientServices.exe'
DEFAULT_RIOT_LOCKFILE = 'C:\\Users\\sandbox\\AppData\\Local\\Riot Games\\Riot Client\\Config\\lockfile'
DEFAULT_LEAGUE_EXE = 'C:\\Riot Games\\League of Legends\\LeagueClient.exe'
DEFAULT_LEAGUE_LOCKFILE = 'C:\\Riot Games\\League of Legends\\lockfile'


def main():
    '''Main function'''
    open_riot_client(DEFAULT_RIOT_EXE)
    riot_connection = LeagueConnection(DEFAULT_RIOT_LOCKFILE)
    res = login(riot_connection, 'your_username', 'your_password')
    if not res['ok']:
        print(res)
        return
    open_league_client(DEFAULT_LEAGUE_EXE)


if __name__ == '__main__':
    main()
```
