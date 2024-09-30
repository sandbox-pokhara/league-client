from typing import Callable
from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS
from league_client.constants import SSL_CONTEXT


def sign_up(
    username: str,
    password: str,
    email: str,
    dob: str,
    captcha_solver: Callable[[str, str], str],
    proxy: Optional[ProxyTypes] = None,
):
    with httpx.Client(
        verify=SSL_CONTEXT,
        proxy=proxy,
        headers={"User-Agent": HEADERS["User-Agent"]},
    ) as client:
        # step 1: setup
        res = client.get(
            r"https://xsso.leagueoflegends.com/login?uri=https://signup.leagueoflegends.com&prompt=signup&show_region=true&locale=en_US",
            follow_redirects=True,
        )
        res.raise_for_status()

        # step 2: get hcaptcha details (sitekey and rqdata)
        res = client.get("https://authenticate.riotgames.com/api/v1/login")
        res.raise_for_status()
        data = res.json()
        site_key = data["captcha"]["hcaptcha"]["key"]
        site_data = data["captcha"]["hcaptcha"]["data"]

        # step 3: solve captcha
        token = captcha_solver(site_data, site_key)

        # step 4: sign up
        data = {
            "type": "signup",
            "username": username,
            "password": password,
            "locale": "en_US",
            "newsletter": False,
            "tou_agree": True,
            "email_address": email,
            "birth_date": dob,
            "captcha": f"hcaptcha {token}",
        }
        res = client.put(
            "https://authenticate.riotgames.com/api/v1/login", json=data
        )
        res.raise_for_status()
        data = res.json()

        # step 5(optional): account is already created at step 4
        # this step is for parsing ssid and clid
        res = client.get(
            data["success"]["redirect_url"],
            headers=HEADERS,
            follow_redirects=True,
        )
        res.raise_for_status()
        ssid = client.cookies["ssid"]
        clid = client.cookies["clid"]
        return ssid, clid
