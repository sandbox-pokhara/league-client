from typing import Any
from typing import List
from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS
from league_client.rso.constants import InventoryTypes


def _inventory_data_from_url(
    inventory_url: str,
    ledge_token: str,
    puuid: str,
    account_id: int,
    service_location: str,
    inventory_types: List[InventoryTypes],
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {ledge_token}"
    res = httpx.get(
        inventory_url,
        headers=h,
        params={
            "puuid": puuid,
            "accountId": account_id,
            "location": service_location,
            "inventoryTypes": [item.value for item in inventory_types],
            "signed": True,
        },
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()["data"]


def get_inventory_data(
    ledge_token: str,
    puuid: str,
    account_id: int,
    service_location: str,
    ledge_url: str,
    inventory_types: List[InventoryTypes],
    proxy: Optional[ProxyTypes] = None,
):
    return _inventory_data_from_url(
        f"{ledge_url}/lolinventoryservice-ledge/v1/inventories/simple",
        ledge_token,
        puuid,
        account_id,
        service_location,
        inventory_types,
        proxy,
    )


def get_inventory_token(inventory_data: dict[str, Any]):
    return inventory_data["itemsJwt"]


def get_inventory_data_v2(
    ledge_token: str,
    puuid: str,
    account_id: int,
    service_location: str,
    ledge_url: str,
    inventory_types: List[InventoryTypes],
    proxy: Optional[ProxyTypes] = None,
):
    return _inventory_data_from_url(
        f"{ledge_url}/lolinventoryservice-ledge/v2/inventoriesWithLoyalty",
        ledge_token,
        puuid,
        account_id,
        service_location,
        inventory_types,
        proxy,
    )


def get_inventory_token_v2(inventory_data_v2: dict[str, Any]):
    return inventory_data_v2["itemsJwt"]
