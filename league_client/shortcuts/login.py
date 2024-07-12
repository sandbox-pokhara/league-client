import os
import time
from typing import Any

import httpx
from ucaptcha import solver  # type:ignore

from league_client.connection import LeagueConnection
from league_client.constants import SITE_URL
from league_client.constants import USER_AGENT
from league_client.exceptions import AccountBannedError
from league_client.exceptions import AgeRestrictedError
from league_client.exceptions import AuthFailureError
from league_client.exceptions import ConsentRequiredError
from league_client.exceptions import CountryRegionMissingError
from league_client.exceptions import EmptyRQDataError
from league_client.exceptions import LCURateLimitedError
from league_client.exceptions import LoginTimeoutError
from league_client.exceptions import LoginTokenError
from league_client.exceptions import NameChangeRequiredError
from league_client.exceptions import NeedsAuthenticationError
from league_client.exceptions import PatchTimeoutError
from league_client.exceptions import RegionMissingError
from league_client.exceptions import UnknownPhaseError
from league_client.exceptions import VNGAccountError
from league_client.exceptions import WrongAccountLoggedInError
from league_client.lcu.username import get_username
from league_client.rcu.auth import accept_agreement
from league_client.rcu.auth import get_is_age_restricted
from league_client.rcu.auth import get_is_agreement_required
from league_client.rcu.auth import get_is_authorized
from league_client.rcu.auth import get_is_country_region_missing
from league_client.rcu.auth import get_rq_data_and_site_key
from league_client.shortcuts import logger
from league_client.shortcuts.logout import logout
from league_client.shortcuts.process import is_running
from league_client.shortcuts.process import open_riot_client

PHASES = {
    "login": [
        "WaitingForAuthentication",
        "WaitingForEula",
        "Done",
        "Disabled",
        "Login",
        "",
    ],
    "wait_for_launch": ["WaitForLaunch"],
    "success": ["WaitForSessionExit"],
    "eula": ["Eula"],
    "consent_required": ["AgeRestriction"],
    "banned": [],
    "account_alias_change": ["AccountAlias"],
    "region_missing": ["HomeBaseCountry"],
    "patch_status": ["PatchStatus", "WaitingForPatchStatus"],
    "vng_account_required": ["VngAccountRequired"],
}


def wait_until_patched(connection: LeagueConnection, timeout: float = 7200):
    start_time = time.time()
    while True:
        try:
            time.sleep(10)
            time_elapsed = time.time() - start_time
            logger.info(
                f"Patching riot client. Time elapsed: {int(time_elapsed)}s."
            )
            if time_elapsed > timeout:
                return False
            res = connection.get("/rnet-lifecycle/v1/product-context-phase")
            phase = res.json()
            if phase not in ["PatchStatus", "WaitingForPatchStatus"]:
                return True
        except httpx.HTTPError:
            pass


def get_captcha_token(
    captcha_api_key: str,
    captcha_service: str,
    rq_data: str,
    site_key: str,
    cookies: dict[str, Any] | None = None,
    user_agent: str = USER_AGENT,
) -> str:
    logger.info(f"Getting captcha token using {captcha_service}...")
    return solver.solve_captcha(  # type: ignore
        captcha_service,
        captcha_api_key,
        site_key,
        SITE_URL,
        user_agent,
        rq_data,
        cookies=cookies,
    )  # type: ignore


def get_login_token(
    connection: LeagueConnection,
    username: str,
    password: str,
    captcha_token: str,
    remember: bool,
):
    logger.info("Posting telemetry...")
    data = {"action": "succeeded", "type": "hcaptcha"}
    res = connection.put(
        "/telemetry/v2/events/riotclient__CaptchaEvent__v2", json=data
    )
    logger.info("Getting login token...")
    data = {
        "username": username,
        "password": password,
        "remember": remember,
        "captcha": f"hcaptcha {captcha_token}",
        "language": "en_GB",
    }
    res = connection.post(
        "/rso-authenticator/v1/authentication/riot-identity/complete",
        json=data,
    )
    res_json = res.json()
    return res_json


def launch_league(connection: LeagueConnection):
    connection.post(
        "/product-launcher/v1/products/league_of_legends/patchlines/live"
    )


def get_product_context_phase(connection: LeagueConnection) -> str:
    res = connection.get("/rnet-lifecycle/v1/product-context-phase")
    if res.status_code == 404:
        return ""
    return res.json()


def authorize(
    connection: LeagueConnection,
    username: str,
    password: str,
    captcha_api_key: str,
    captcha_service: str,
    persist_login: bool = False,
    user_agent: str = USER_AGENT,
):
    authorized = get_is_authorized(connection)

    if authorized:
        if get_is_age_restricted(connection):
            raise AgeRestrictedError
        if get_is_country_region_missing(connection):
            raise CountryRegionMissingError
        return True
    if authorized and get_is_agreement_required(connection):
        accept_agreement(connection)
        return True

    rq_and_site_key_data = get_rq_data_and_site_key(connection)

    if rq_and_site_key_data is None:
        logger.info("Cannot fetch rq and site key data.")
        return EmptyRQDataError
    site_key = rq_and_site_key_data["key"]
    rq_data = rq_and_site_key_data["data"]

    captcha_token = get_captcha_token(
        captcha_api_key=captcha_api_key,
        captcha_service=captcha_service,
        rq_data=rq_data,
        site_key=site_key,
        user_agent=user_agent,
    )

    login_token_response = get_login_token(
        connection,
        username,
        password,
        captcha_token,
        remember=persist_login,
    )

    # Check if needs to redo captcha
    if "captcha_not_allowed" in login_token_response.get("error", ""):
        logger.info(f"Captcha not allowed. Resolving captcha...")
        site_key = login_token_response["captcha"]["hcaptcha"]["key"]
        rq_data = login_token_response["captcha"]["hcaptcha"]["data"]

        captcha_token = get_captcha_token(
            captcha_service=captcha_service,
            captcha_api_key=captcha_api_key,
            rq_data=rq_data,
            site_key=site_key,
            user_agent=user_agent,
        )

        login_token_response = get_login_token(
            connection,
            username,
            password,
            captcha_token,
            remember=persist_login,
        )

    if login_token_response.get("error"):
        raise LoginTokenError(login_token_response.get("error"))

    login_token = login_token_response.get("success", {}).get(
        "login_token", ""
    )
    if not login_token:
        raise AuthFailureError

    logger.info(f"Patching login token...")
    data = {
        "authentication_type": "RiotAuth",
        "login_token": login_token,
        "persist_login": persist_login,
    }

    res = connection.put("/rso-auth/v1/session/login-token", json=data)
    res_json = res.json()
    if not res_json.get("type") == "authenticated":
        raise AuthFailureError

    logger.info("Posting authorizations...")
    data = {"clientId": "riot-client", "trustLevels": ["always_trusted"]}
    res = connection.post("/rso-auth/v2/authorizations", json=data)
    res_json = res.json()

    if res_json.get("type") == "authorized":
        return True

    if res_json.get("type") == "needs_authentication":
        raise NeedsAuthenticationError

    if "message" in res_json:
        if res_json["message"] == "authorization_error: consent_required: ":
            raise ConsentRequiredError
    if "error" in res_json:
        if res_json["error"] == "auth_failure":
            raise AuthFailureError
        if res_json["error"] == "rate_limited":
            raise LCURateLimitedError
    return False


def rcu_login(
    riot_connection: LeagueConnection,
    username: str,
    password: str,
    captcha_api_key: str,
    captcha_service: str,
    persist_login: bool = False,
    timeout: float = 180,
    patch_timeout: float = 7200,
    user_agent: str = USER_AGENT,
):
    logger.info("Logging in...")
    start_time = time.time()

    while True:
        if time.time() - start_time >= timeout:
            raise LoginTimeoutError

        phase = get_product_context_phase(riot_connection)
        logger.info(f"Riot client phase: {phase}")

        # Bad phases
        if phase == "Unknown":
            raise UnknownPhaseError
        if phase in PHASES["region_missing"]:
            raise RegionMissingError
        if phase in PHASES["banned"]:
            raise AccountBannedError
        if phase in PHASES["consent_required"]:
            raise ConsentRequiredError
        if phase in PHASES["account_alias_change"]:
            raise NameChangeRequiredError
        if phase in PHASES["vng_account_required"]:
            raise VNGAccountError

        # Good phases
        if phase in PHASES["success"]:
            if is_running("LeagueClient.exe"):
                return
            launch_league(riot_connection)
            time.sleep(2)
            continue
        if phase in PHASES["wait_for_launch"]:
            launch_league(riot_connection)
            time.sleep(2)
            continue
        if phase in PHASES["login"]:
            complete = authorize(
                riot_connection,
                username,
                password,
                persist_login=persist_login,
                captcha_service=captcha_service,
                captcha_api_key=captcha_api_key,
                user_agent=user_agent,
            )
            if complete:
                if is_running("LeagueClient.exe"):
                    return
                launch_league(riot_connection)
                time.sleep(2)
                continue
            else:
                time.sleep(2)
                continue
        if phase in PHASES["eula"]:
            accept_agreement(riot_connection)
            time.sleep(2)
            continue
        if phase in PHASES["patch_status"]:
            if not wait_until_patched(riot_connection, timeout=patch_timeout):
                raise PatchTimeoutError
            time.sleep(2)
            continue
        time.sleep(2)


def check_username(
    connection: LeagueConnection, expected_username: str, timeout: float = 20
):
    logger.info("Checking username...")
    start = time.time()
    while True:
        if time.time() - start > timeout:
            raise LoginTimeoutError
        username_client = get_username(connection)
        if username_client is None or username_client == "":
            time.sleep(1)
            continue
        if expected_username.lower() == username_client.lower():
            return
        raise WrongAccountLoggedInError


def wait_session_in_progress(
    connection: LeagueConnection, timeout: float = 180
):
    start = time.time()
    while True:
        if time.time() - start > timeout:
            return False
        res = connection.get("/lol-login/v1/session")
        if res.status_code == 404:
            return True
        if res.json()["state"] != "IN_PROGRESS":
            return
        time.sleep(1)


def wait_session(
    riot_lockfile: str,
    league_lockfile: str,
    timeout: float = 60,
    in_progress_timeout: float = 180,
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
        except httpx.HTTPError:
            time.sleep(1)


def login(
    username: str,
    password: str,
    captcha_service: str,
    captcha_api_key: str,
    riot_exe: str,
    riot_lockfile: str,
    league_lockfile: str,
):
    """
    Logs into riot client and waits for league client session and switches
    account if wrong account is logged in
    """
    while True:
        try:
            logger.info("Starting riot client...")
            open_riot_client(riot_exe)
            logger.info("Connecting to riot client...")
            riot_connection = LeagueConnection(riot_lockfile)
            rcu_login(
                riot_connection,
                username=username,
                password=password,
                captcha_api_key=captcha_api_key,
                captcha_service=captcha_service,
            )
            wait_session(riot_lockfile, league_lockfile)
            league_connection = LeagueConnection(league_lockfile)
            try:
                check_username(league_connection, username)
            except WrongAccountLoggedInError:
                logger.info("Changing account...")
                logout(league_lockfile)
                continue
            return
        except httpx.HTTPError:
            logger.exception("HTTPError")
