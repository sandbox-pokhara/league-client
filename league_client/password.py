import re
from copy import copy

from league_client.exceptions import RSOAuthorizeError

from .logger import logger
from .rso import HEADERS
from .rso import ClientSession
from .rso import get_basic_auth
from .rso_auth import parsing_auth_code
from .rso_auth import rso_authorize

accountodactyl = {
    "scope": (
        "openid email profile riot://riot.atlas/accounts.edit"
        " riot://riot.atlas/accounts/password.edit"
        " riot://riot.atlas/accounts/email.edit"
        " riot://riot.atlas/accounts.auth riot://third_party.revoke"
        " riot://third_party.query riot://forgetme/notify.write"
        " riot://riot.authenticator/auth.code"
        " riot://riot.authenticator/authz.edit riot://rso/mfa/device.write"
        " riot://riot.authenticator/identity.add"
    ),
    "state": "fc5a8f17-e99f-4eb9-afd9-a950e0eb30c6",
    "acr_values": "urn:riot:gold",
    "ui_locales": "en",
    "client_id": "accountodactyl-prod",
    "redirect_uri": "https://account.riotgames.com/oauth2/log-in",
    "response_type": "code",
}


async def redirect(session, url, proxy, proxy_user=None, proxy_pass=None):
    async with session.get(
        url,
        proxy=proxy,
        proxy_auth=get_basic_auth(proxy_user, proxy_pass),
        headers=HEADERS,
    ) as res:
        return res.ok


async def get_csrf_token(session, proxy, proxy_user=None, proxy_pass=None):
    async with session.get(
        "https://account.riotgames.com/",
        proxy=proxy,
        proxy_auth=get_basic_auth(proxy_user, proxy_pass),
        headers=HEADERS,
    ) as res:
        if not res.ok:
            return None
        text = await res.text()
        pattern = (
            "<meta name=['\"]csrf-token['\"] content=['\"](.{36})['\"] />"
        )
        match = re.search(pattern, text)
        if match is None:
            return None
        return match.group(1)


async def initialize_account_manager_session(
    session, username, password, proxy, proxy_user, proxy_pass
):
    """RSO login and returns csrf_token in the provided session"""
    proxy_auth = get_basic_auth(proxy_user, proxy_pass)
    if not await parsing_auth_code(
        session, accountodactyl, proxy, proxy_user, proxy_pass
    ):
        return None
    data = await rso_authorize(session, username, password, proxy, proxy_auth)
    url = data["response"]["parameters"]["uri"]
    if url is None:
        return None

    if not await redirect(session, url, proxy, proxy_user, proxy_pass):
        return None

    csrf_token = await get_csrf_token(session, proxy, proxy_user, proxy_pass)
    if csrf_token is None:
        return None

    return csrf_token


async def post_change_password(
    session,
    csrf_token,
    current_password,
    new_password,
    proxy,
    proxy_user=None,
    proxy_pass=None,
):
    data = {
        "currentPassword": current_password,
        "password": new_password,
    }
    headers = copy(HEADERS)
    headers["csrf-token"] = csrf_token
    # If referer is not set, it responseds with 403, not logged in error
    headers["referer"] = "https://account.riotgames.com/"
    async with session.put(
        "https://account.riotgames.com/api/account/v1/user/password",
        proxy=proxy,
        proxy_auth=get_basic_auth(proxy_user, proxy_pass),
        json=data,
        headers=headers,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            logger.debug(await res.text())
        return res.ok


async def post_send_verify_link(
    session,
    csrf_token,
    email,
    proxy,
    proxy_user=None,
    proxy_pass=None,
):
    data = {
        "email": email,
    }
    headers = copy(HEADERS)
    headers["csrf-token"] = csrf_token
    headers["referer"] = "https://account.riotgames.com/"
    async with session.post(
        "https://account.riotgames.com/api/account/v1/user/email/",
        proxy=proxy,
        proxy_auth=get_basic_auth(proxy_user, proxy_pass),
        json=data,
        headers=headers,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            logger.debug(await res.text())
            return False
        return True


async def post_change_password_and_send_verify_link(
    session,
    csrf_token,
    current_password,
    new_password,
    email,
    proxy,
    proxy_user=None,
    proxy_pass=None,
):
    data1 = {
        "currentPassword": current_password,
        "password": new_password,
    }
    data2 = {
        "email": email,
    }
    headers = copy(HEADERS)
    headers["csrf-token"] = csrf_token
    # If referer is not set, it responseds with 403, not logged in error
    headers["referer"] = "https://account.riotgames.com/"
    async with session.put(
        "https://account.riotgames.com/api/account/v1/user/password",
        proxy=proxy,
        proxy_auth=get_basic_auth(proxy_user, proxy_pass),
        json=data1,
        headers=headers,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            logger.debug(await res.text())
            return False, False
    async with session.post(
        "https://account.riotgames.com/api/account/v1/user/email/",
        proxy=proxy,
        proxy_auth=get_basic_auth(proxy_user, proxy_pass),
        json=data2,
        headers=headers,
    ) as res:
        if not res.ok:
            logger.debug(res.status)
            logger.debug(await res.text())
            return True, False
        return True, True


async def change_password(
    username,
    password,
    new_password,
    proxy=None,
    proxy_user=None,
    proxy_pass=None,
):
    async with ClientSession() as session:
        csrf_token = await initialize_account_manager_session(
            session, username, password, proxy, proxy_user, proxy_pass
        )
        if csrf_token is None:
            return False

        if not await post_change_password(
            session,
            csrf_token,
            password,
            new_password,
            proxy,
            proxy_user,
            proxy_pass,
        ):
            return False
        return True


async def check_password(
    username,
    password,
    proxy=None,
    proxy_user=None,
    proxy_pass=None,
):
    """Check whether the password is correct

    Args:
        username (str): account username
        password (str): account password
        email (str): valid email address to send the verify link to
        proxy (str, optional): proxy url. Defaults to None.
        proxy_user (str, optional): proxy username. Defaults to None.
        proxy_pass (str, optional): proxy password. Defaults to None.

    Returns:
        True: password is correct
        False: password is incorrect
    """
    async with ClientSession() as session:
        proxy_auth = get_basic_auth(proxy_user, proxy_pass)
        if not await parsing_auth_code(
            session, accountodactyl, proxy, proxy_user, proxy_pass
        ):
            return False
        try:
            await rso_authorize(session, username, password, proxy, proxy_auth)
        except RSOAuthorizeError as e:
            if e.code == "WRONG_PASSWORD":
                return False
            raise
        return True


async def send_verify_link(
    username, password, email, proxy=None, proxy_user=None, proxy_pass=None
):
    """Send verify link to email (doesn't verify the email)

    Args:
        username (str): account username
        password (str): account password
        email (str): valid email address to send the verify link to
        proxy (str, optional): proxy url. Defaults to None.
        proxy_user (str, optional): proxy username. Defaults to None.
        proxy_pass (str, optional): proxy password. Defaults to None.

    Returns:
        False: Failed to send the verify link
        True: Successfully sent the verify link
    """
    async with ClientSession() as session:
        csrf_token = await initialize_account_manager_session(
            session, username, password, proxy, proxy_user, proxy_pass
        )
        if csrf_token is None:
            return False

        if not await post_send_verify_link(
            session,
            csrf_token,
            email,
            proxy,
            proxy_user,
            proxy_pass,
        ):
            return False
        return True


async def change_password_and_send_verify_link(
    username,
    password,
    new_password,
    email,
    proxy=None,
    proxy_user=None,
    proxy_pass=None,
):
    """Change password and send verify link to email

    Args:
        username (str): account username
        password (str): account password
        new_password (str): new password to change to
        email (str): valid email address to send the verify link to
        proxy (str, optional): proxy url. Defaults to None.
        proxy_user (str, optional): proxy username. Defaults to None.
        proxy_pass (str, optional): proxy password. Defaults to None.

    Returns:
        (bool, bool): (password_changed, verify_link_sent)
        # NOTE (True, False): password is changed but verify link could not be sent
    """
    async with ClientSession() as session:
        csrf_token = await initialize_account_manager_session(
            session, username, password, proxy, proxy_user, proxy_pass
        )
        if csrf_token is None:
            return False, False

        return await post_change_password_and_send_verify_link(
            session,
            csrf_token,
            password,
            new_password,
            email,
            proxy,
            proxy_user,
            proxy_pass,
        )
