import os
import time

import requests
from league_connection import LeagueConnection

from league_process.utils import is_running

from .logger import logger
from .login import launch_league


def wait_session_in_progress(connection, timeout=180):
    start = time.time()
    while True:
        if time.time() - start > timeout:
            return False
        res = connection.get("/lol-login/v1/session")
        if not res.ok:
            return True
        if res.json()["state"] != "IN_PROGRESS":
            return True
        time.sleep(1)


def wait_session(riot_lockfile, league_lockfile, timeout=60, in_progress_timeout=180):
    start = time.time()
    logger.info("Waiting for session...")
    while True:
        try:
            if time.time() - start > timeout:
                return {"ok": False, "detail": "Timeout."}
            riot_connection = LeagueConnection(riot_lockfile)
            if not is_running("LeagueClient.exe") or not os.path.isfile(
                league_lockfile
            ):
                launch_league(riot_connection)
                time.sleep(1)
                continue
            league_connection = LeagueConnection(league_lockfile)
            res = league_connection.get("/lol-login/v1/session")
            if res.status_code == 404:
                time.sleep(1)
                continue
            res = res.json()
            state = res["state"]
            logger.info(f"Session state: {state}")
            if state == "SUCCEEDED":
                return {"ok": True}
            if state == "IN_PROGRESS":
                if not wait_session_in_progress(
                    league_connection, timeout=in_progress_timeout
                ):
                    return {"ok": False, "detail": "In progress timeout."}
            if res.get("isNewPlayer", False):
                return {"ok": False, "detail": "New player."}
            if state == "ERROR":
                if res["error"]["messageId"] == "ACCOUNT_BANNED":
                    return {"ok": False, "detail": "Account banned."}
                return {"ok": False, "detail": res["error"]["messageId"]}
            time.sleep(1)
        except requests.exceptions.RequestException:
            time.sleep(1)
