import os
import time
import typing
from urllib.parse import urljoin

from httpx import Client
from httpx.__version__ import __version__
from httpx._models import Response
from httpx._types import URLTypes

from league_client.exceptions import LCUConnectionError

LCU_LOCKFILE = os.path.expanduser(
    "~\\AppData\\Local\\Riot Games\\Riot Client\\Config\\lockfile"
)


class LeagueConnection(Client):
    def __init__(self, lockfile: str = LCU_LOCKFILE, timeout: float = 30):
        super().__init__(verify=False)
        start = time.time()
        while True:
            if time.time() - start > timeout:
                raise LCUConnectionError(
                    "Please make sure the client is running."
                )
            if not os.path.exists(lockfile):
                time.sleep(1)
                continue
            with open(lockfile, "r") as fp:
                data = fp.read()
                data = data.split(":")

                if len(data) < 5:
                    time.sleep(1)
                    continue
                self.url = f"{data[4]}://127.0.0.1:{data[2]}"
                self.username = "riot"
                self.password = data[3]
                break

    def request(
        self,
        method: str,
        url: URLTypes,
        **kwargs: typing.Any,
    ) -> Response:
        kwargs["url"] = urljoin(self.url, str(url))
        kwargs["auth"] = self.username, self.password
        return super().request(method, **kwargs)
