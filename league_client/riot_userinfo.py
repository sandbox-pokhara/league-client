import aiohttp

from league_client.password import get_csrf_token
from league_client.rso import HEADERS
from league_client.rso import get_basic_auth
from league_client.rso_auth import parsing_auth_code
from league_client.rso_auth import rso_authorize
from league_client.rso_userinfo import parse_accountinfo

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


async def get_riot_userinfo(
    username, password, proxy=None, proxy_user=None, proxy_pass=None
):
    async with aiohttp.ClientSession() as session:
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

        return await parse_accountinfo(
            session,
            csrf_token,
            proxy,
            proxy_user,
            proxy_pass,
        )
