import re
from copy import copy

from .logger import logger
from .rso import HEADERS
from .rso import ClientSession
from .rso import get_basic_auth
from .rso_auth import parsing_auth_code
from .rso_auth import rso_authorize

accountodactyl = {
    "scope": "openid email profile riot://riot.atlas/accounts.edit riot://riot.atlas/accounts/password.edit riot://riot.atlas/accounts/email.edit riot://riot.atlas/accounts.auth riot://third_party.revoke riot://third_party.query riot://forgetme/notify.write riot://riot.authenticator/auth.code riot://riot.authenticator/authz.edit riot://rso/mfa/device.write riot://riot.authenticator/identity.add",
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
        pattern = "<meta name=['\"]csrf-token['\"] content=['\"](.{36})['\"] />"
        match = re.search(pattern, text)
        if match is None:
            return None
        return match.group(1)


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


async def change_password(
    username, password, new_password, proxy=None, proxy_user=None, proxy_pass=None
):
    async with ClientSession() as session:
        proxy_auth = get_basic_auth(proxy_user, proxy_pass)
        if not await parsing_auth_code(
            session, accountodactyl, proxy, proxy_user, proxy_pass
        ):
            return False
        data = await rso_authorize(session, username, password, proxy, proxy_auth)
        url = data["response"]["parameters"]["uri"]
        if url is None:
            return False

        if not await redirect(session, url, proxy, proxy_user, proxy_pass):
            return False

        csrf_token = await get_csrf_token(session, proxy, proxy_user, proxy_pass)
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
