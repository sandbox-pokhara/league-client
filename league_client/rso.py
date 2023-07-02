import ssl

import aiohttp

from .logger import logger

# https://developers.cloudflare.com/ssl/ssl-tls/cipher-suites/
FORCED_CIPHERS = [
    "ECDHE-ECDSA-AES256-GCM-SHA384",
    "ECDHE-ECDSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-CHACHA20-POLY1305",
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-RSA-CHACHA20-POLY1305",
    "ECDHE-RSA-AES128-SHA256",
    "ECDHE-RSA-AES128-SHA",
    "ECDHE-RSA-AES256-SHA" "ECDHE-ECDSA-AES128-SHA256",
    "ECDHE-ECDSA-AES128-SHA",
    "ECDHE-ECDSA-AES256-SHA",
    "ECDHE+AES128",
    "ECDHE+AES256",
    "ECDHE+3DES",
    "RSA+AES128",
    "RSA+AES256",
    "RSA+3DES",
]

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}


class ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.set_ciphers(":".join(FORCED_CIPHERS))
        super().__init__(
            *args,
            **kwargs,
            cookie_jar=aiohttp.CookieJar(),
            connector=aiohttp.TCPConnector(verify_ssl=False)
        )


def get_basic_auth(proxy_user, proxy_pass):
    if proxy_user is not None and proxy_pass is not None:
        return aiohttp.BasicAuth(proxy_user, proxy_pass)
    return None
