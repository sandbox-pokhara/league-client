import re
from typing import Callable
from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import ACCOUNTODACTYL_PARAMS
from league_client.constants import HEADERS
from league_client.constants import PROD_XSS0_RIOTGAMES
from league_client.constants import SSL_CONTEXT
from league_client.rso.auth import authorize


def parse_csrf_token(text: str):
    pattern = "<meta name=['\"]csrf-token['\"] content=['\"](.{36})['\"] />"
    match = re.search(pattern, text)
    if match is None:
        return None
    return match.group(1)


def change_password_using_credentials(
    username: str,
    password: str,
    new_password: str,
    captcha_solver: Callable[[str, str], str],
    proxy: Optional[ProxyTypes] = None,
) -> bool:
    with httpx.Client(verify=SSL_CONTEXT, proxy=proxy) as client:
        authorize(
            client, username, password, captcha_solver, PROD_XSS0_RIOTGAMES
        )
        authorize(
            client,
            username,
            password,
            captcha_solver,
            ACCOUNTODACTYL_PARAMS,
            "re-auth",
        )
        res = client.get(
            "https://account.riotgames.com/",
            headers=HEADERS,
            follow_redirects=True,
        )
        csrf_token = parse_csrf_token(res.text)
        if csrf_token is None:
            return False
        data = {
            "currentPassword": password,
            "password": new_password,
        }
        headers = HEADERS.copy()
        headers["csrf-token"] = csrf_token
        headers["referer"] = "https://account.riotgames.com/"
        res = client.put(
            "https://account.riotgames.com/api/account/v1/user/password",
            headers=headers,
            json=data,
        )
        res.raise_for_status()
        data = res.json()
        if "message" in data:
            if data["message"] == "password_updated":
                return True
        return False
