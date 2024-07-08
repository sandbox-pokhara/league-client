import os
import time

import httpx
from league_connection import LeagueConnection

from league_client.lcu.login import launch_league
from league_client.logger import logger
from league_process.utils import is_running


def wait_session_in_progress(
    connection: httpx.Client, timeout: int = 180
) -> bool:
    start = time.time()
    while True:
        if time.time() - start > timeout:
            return False
        try:
            res = connection.get("/lol-login/v1/session")
            res.raise_for_status()
            if res.json()["state"] != "IN_PROGRESS":
                return True
        except (httpx.HTTPStatusError, httpx.RequestError):
            return True
        time.sleep(1)


def wait_session(
    riot_lockfile: str,
    league_lockfile: str,
    timeout: int = 60,
    in_progress_timeout: int = 180,
):
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
        except httpx.RequestError:
            time.sleep(1)
