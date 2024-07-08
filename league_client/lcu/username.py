import time

import httpx

from league_client.logger import logger


def get_username(connection: httpx.Client):
    try:
        res = connection.get("/lol-login/v1/login-platform-credentials")
        res.raise_for_status()
        return res.json().get("username")
    except (httpx.HTTPStatusError, httpx.RequestError):
        return None


def check_username(
    connection: httpx.Client, expected_username: str, timeout: int = 20
):
    logger.info("Checking username...")
    start = time.time()
    while True:
        if time.time() - start > timeout:
            return {"ok": False, "detail": "Timeout."}
        username_client = get_username(connection)
        if username_client is None or username_client == "":
            time.sleep(1)
            continue
        if expected_username.lower() == username_client.lower():
            return {"ok": True}
        return {"ok": False, "detail": "Wrong username."}
