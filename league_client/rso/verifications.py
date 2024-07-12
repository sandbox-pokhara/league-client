from league_client.rso.utils import decode_token


def get_is_phone_verified(id_token: str) -> bool:
    decoded_id_token = decode_token(id_token)
    return bool(decoded_id_token["phone_number_verified"])


def get_is_email_verified(id_token: str) -> bool:
    decoded_id_token = decode_token(id_token)
    return bool(decoded_id_token["account_verified"])
