import requests
from league_connection import LeagueConnection

from league_process.process import open_riot_client

from .logger import logger
from .login import authorize
from .logout import logout
from .session import wait_session
from .username import check_username


def login(
    username,
    password,
    captcha_api_key,
    captcha_service,
    riot_exe,
    riot_lockfile,
    league_lockfile,
):
    while True:
        try:
            open_riot_client(riot_exe)
            riot_connection = LeagueConnection(riot_lockfile)
            res = authorize(
                riot_connection,
                username=username,
                password=password,
                captcha_service=captcha_service,
                captcha_api_key=captcha_api_key,
            )
            if not res["ok"]:
                return res
            res = wait_session(riot_lockfile, league_lockfile)
            if not res["ok"]:
                return res
            league_connection = LeagueConnection(league_lockfile)
            res = check_username(league_connection, username)
            if not res["ok"]:
                if res["detail"] == "Wrong username.":
                    logger.info("Changing account...")
                    logout(league_lockfile)
                    continue
                return res
            return {"ok": True}
        except requests.RequestException:
            logger.info("RequestException")
