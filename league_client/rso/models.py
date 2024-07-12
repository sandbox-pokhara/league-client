from typing import Any
from typing import Optional
from urllib.parse import urljoin

from pydantic import BaseModel

from league_client.rso.constants import DISCOVEROUS_SERVICE_LOCATION
from league_client.rso.constants import LEAGUE_EDGE_URL
from league_client.rso.constants import PLAYER_PLATFORM_EDGE_URL


class RSOSession(BaseModel):

    ssid: str = ""
    access_token: str = ""
    scope: str = ""
    iss: str = ""
    id_token: str = ""
    token_type: str = ""
    session_state: str = ""
    expires_in: str = ""

    puuid: str = ""
    region: str = ""
    account_id: int = -1

    userinfo: str | dict[Any, Any] = {}

    # tokens
    login_queue_token: str = ""
    ledge_token: str = ""
    event_inventory_token: str = ""
    champion_inventory_token: str = ""

    proxy: Optional[str] = None

    def get_ledge_url(self, path: str = ""):
        return urljoin(LEAGUE_EDGE_URL[self.region], path)

    def get_player_platform_edge_url(self, path: str = ""):
        return urljoin(PLAYER_PLATFORM_EDGE_URL[self.region], path)

    def get_discoverous_service_location(self, path: str = ""):
        return urljoin(DISCOVEROUS_SERVICE_LOCATION[self.region], path)
