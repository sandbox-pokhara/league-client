# league-client

league-client is a python package to communicate with riot client and league client.

## Installation

```
pip install league-client
```

## Known Limitations

- RSO does not work in python3.6

## Example

### Define paths

```
>>> riot_exe = 'C:\\Riot Games\\Riot Client\\RiotClientServices.exe'
>>> riot_lockfile = 'C:\\Users\\sandbox\\AppData\\Local\\Riot Games\\Riot Client\\Config\\lockfile'
>>> league_lockfile = 'C:\\Riot Games\\League of Legends\\lockfile'
```

### Log in

```
>>> from league_client.shortcuts import login
>>> login(
...         'username',
...         'password',
...         riot_exe,
...         riot_lockfile,
...         league_lockfile,
...         captcha_service,
...         captcha_api_key,
...     )
05/10/2022 12:18:09 PM - INFO - Logging in...
05/10/2022 12:18:18 PM - INFO - Waiting for session...
05/10/2022 12:18:22 PM - INFO - Session state: IN_PROGRESS
05/10/2022 12:18:28 PM - INFO - Session state: SUCCEEDED
05/10/2022 12:18:28 PM - INFO - Checking username...
{'ok': True}
```

### Change Log

- Add option to pass custom user agent and cookies.
