import asyncio
import json
import os
import time

import requests
from ucaptcha import solver
from ucaptcha.exceptions import CaptchaException
from ucaptcha.exceptions import KeyDoesNotExistException
from ucaptcha.exceptions import WrongUserKeyException
from ucaptcha.exceptions import ZeroBalanceException

from league_client.constants import SITE_URL
from league_client.constants import USER_AGENT
from league_process.utils import is_running

from .logger import logger


def get_rq_data_and_site_key(connection):
    connection.delete("/rso-authenticator/v1/authentication")
    res = connection.post(
        "/rso-authenticator/v1/authentication/riot-identity/start",
        json={
            "language": "en_GB",
            "productId": "riot-client",
            "state": "auth",
        },
    )
    if res.ok:
        return res.json()["captcha"]["hcaptcha"]


def get_phases():
    dirname = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dirname, "phases.json")) as fp:
        return json.load(fp)


def get_is_authorized(connection):
    res = connection.get("/rso-auth/v1/authorization")
    return res.ok


def get_is_agreement_required(connection):
    res = connection.get("/eula/v1/agreement")
    if not res.ok:
        return False
    res = res.json()
    if "acceptance" not in res:
        return False
    return res["acceptance"] not in ["Accepted", "WaitingForAllServiceData"]


def get_is_age_restricted(connection):
    try:
        response = connection.get(
            "/age-restriction/v1/age-restriction/products/league_of_legends"
        )
        response = response.json()
        return response.get("restricted", False)
    except (
        json.decoder.JSONDecodeError,
        requests.exceptions.RequestException,
    ):
        return False


def get_is_country_region_missing(connection):
    try:
        response = connection.get("/riot-client-auth/v1/userinfo")
        response = response.json()
        return response.get("country", "npl") == "nan"
    except (
        json.decoder.JSONDecodeError,
        requests.exceptions.RequestException,
    ):
        return False


def accept_agreement(connection):
    connection.put("/eula/v1/agreement/acceptance")


def wait_until_patched(connection, timeout=7200):
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
        except requests.exceptions.RequestException:
            pass


def get_captcha_token(
    connection, captcha_service, captch_api_key, cookies=None
):
    rq_and_site_key_data = get_rq_data_and_site_key(connection)
    if rq_and_site_key_data is None:
        logger.info("Cannot fetch rq and site key data.")
        return None
    site_key = rq_and_site_key_data["key"]
    rq_data = rq_and_site_key_data["data"]
    return solver.solve_captcha(
        captcha_service,
        captch_api_key,
        site_key,
        SITE_URL,
        USER_AGENT,
        rq_data,
        cookies=cookies,
    )


def authorize(
    connection,
    username,
    password,
    captcha_service,
    captcha_api_key,
    cookies=None,
):
    authorized = get_is_authorized(connection)

    if authorized:
        if get_is_age_restricted(connection):
            return {"ok": False, "detail": "Age restricted."}
        if get_is_country_region_missing(connection):
            return {"ok": False, "detail": "Country/region missing."}
        return {"ok": True, "logged_in": True}
    if authorized and get_is_agreement_required(connection):
        accept_agreement(connection)
        return {"ok": True, "logged_in": True}

    captcha_token = None
    try:
        if captcha_api_key is not None:
            logger.info(f"Getting captcha token using {captcha_service}...")
            captcha_token = get_captcha_token(
                connection, captcha_service, captcha_api_key, cookies
            )
            if captcha_token is None:
                return {"ok": False, "detail": "None Captcha"}
    except (
        KeyDoesNotExistException,
        WrongUserKeyException,
        ZeroBalanceException,
    ) as exp:
        logger.info(f"Captcha Error:  {exp.__class__.__name}")
        return {
            "ok": False,
            "detail": f"Captcha Exception: {exp.__class__.__name}",
        }
    except CaptchaException as exp:
        logger.info(f"Captcha Error: {exp}")
        return {"ok": False, "detail": f"Captcha Exception: {str(exp)}"}

    logger.info("Getting login token...")
    data = {
        "username": username,
        "password": password,
        "remember": False,
        "captcha": f"hcaptcha {captcha_token}",
    }

    res = connection.post(
        "/rso-authenticator/v1/authentication/riot-identity/complete",
        json=data,
    )
    res_json = res.json()
    logger.debug(res_json)

    if "auth_failure" in res_json.get("error"):
        return {"ok": False, "detail": "Auth failure."}

    login_token = res_json.get("success", {}).get("login_token", "")
    if not login_token:
        return {"ok": False, "detail": "Auth failure."}

    logger.info(f"Patching login token...")
    data = {
        "authentication_type": "RiotAuth",
        "login_token": login_token,
        "persist_login": False,
    }

    res = connection.put("/rso-auth/v1/session/login-token", json=data)
    res_json = res.json()
    logger.debug(res_json)
    if not res_json.get("type") == "authenticated":
        return {"ok": False, "detail": "Auth failure."}

    logger.info("Posting authorizations...")
    data = {"clientId": "riot-client", "trustLevels": ["always_trusted"]}
    res = connection.post("/rso-auth/v2/authorizations", json=data)
    res_json = res.json()
    logger.debug(res_json)

    if res_json.get("type") == "authorized":
        return {"ok": True, "logged_in": True}

    if res_json.get("type") == "needs_authentication":
        return {"ok": False, "detail": "needs_authentication"}

    if "message" in res_json:
        if res_json["message"] == "authorization_error: consent_required: ":
            return {"ok": False, "detail": "Consent required."}
    if "error" in res_json:
        if res_json["error"] == "auth_failure":
            return {"ok": False, "detail": "Auth failure."}
        if res_json["error"] == "rate_limited":
            return {"ok": False, "detail": "Rate limited."}
    return {"ok": True, "logged_in": False}


def launch_league(connection):
    connection.post(
        "/product-launcher/v1/products/league_of_legends/patchlines/live"
    )


def get_product_context_phase(connection):
    res = connection.get("/rnet-lifecycle/v1/product-context-phase")
    if res.status_code == 404:
        return None
    return res.json()


def login(
    connection,
    username,
    password,
    timeout=180,
    patch_timeout=7200,
    captcha_service=None,
    captcha_api_key=None,
):
    logger.info("Logging in...")
    start_time = time.time()
    phases = get_phases()
    while True:
        if time.time() - start_time >= timeout:
            return {"ok": False, "detail": "Timeout."}

        phase = get_product_context_phase(connection)
        logger.info(f"Riot client phase: {phase}")

        # Bad phases
        if phase == "Unknown":
            return {"ok": False, "detail": "Unknown phase."}
        if phase in phases["region_missing"]:
            return {"ok": False, "detail": "Region missing."}
        if phase in phases["banned"]:
            return {"ok": False, "detail": "Account banned."}
        if phase in phases["consent_required"]:
            return {"ok": False, "detail": "Consent required."}
        if phase in phases["account_alias_change"]:
            return {"ok": False, "detail": "Name change required."}
        if phase in phases["vng_account_required"]:
            return {"ok": False, "detail": "Vng account required."}

        # Good phases
        if phase in phases["success"]:
            if is_running("LeagueClient.exe"):
                return {"ok": True}
            launch_league(connection)
            time.sleep(2)
            continue
        if phase in phases["wait_for_launch"]:
            launch_league(connection)
            time.sleep(2)
            continue
        if phase is None or phase in phases["login"]:
            res = authorize(
                connection,
                username,
                password,
                captcha_service=captcha_service,
                captcha_api_key=captcha_api_key,
            )
            if not res["ok"]:
                return res
            if res["ok"] and res["logged_in"]:
                if is_running("LeagueClient.exe"):
                    return {"ok": True}
                launch_league(connection)
                time.sleep(2)
                continue
            if res["ok"] and not res["logged_in"]:
                time.sleep(2)
                continue
        if phase in phases["eula"]:
            accept_agreement(connection)
            time.sleep(2)
            continue
        if phase in phases["patch_status"]:
            if not wait_until_patched(connection, timeout=patch_timeout):
                return {"ok": False, "detail": "Patch timeout."}
            time.sleep(2)
            continue
        time.sleep(2)
