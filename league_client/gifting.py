import requests

gift_url = "https://euw.store.leagueoflegends.com/storefront/v3/gift?language=en_GB"


def get_giftable_friends(connection):
    res = connection.get("/lol-store/v1/giftablefriends")
    if res.ok:
        return res.json()
    return []


def post_gift(
    token,
    sender_account_id,
    recipient,
    message,
    category_id,
    inventory_type,
    item_id,
    rp,
    quantity=1,
):
    data = {
        "customMessage": message,
        "receiverSummonerId": recipient,
        "giftItemId": category_id,
        "accountId": sender_account_id,
        "items": [
            {
                "inventoryType": inventory_type,
                "itemId": item_id,
                "ipCost": None,
                "rpCost": rp,
                "quantity": quantity,
            }
        ],
    }
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(gift_url, headers=headers, json=data, timeout=30)
    return res.ok
