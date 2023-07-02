import time

from .logger import logger


def get_username(connection):
    res = connection.get("/lol-login/v1/login-platform-credentials")
    if not res.ok:
        return None
    return res.json().get("username")


def check_username(connection, expected_username, timeout=20):
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
