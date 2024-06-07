import jwt

from league_client.constants import CHAT_AFFINITY_DOMAINS
from league_client.constants import CHAT_HOSTS
from league_client.exceptions import AffnityDomainNotFound
from league_client.exceptions import ChatHostNotFound


def get_chat_affinity_server(pas_token: str):
    data = jwt.decode(  # type: ignore
        pas_token, algorithms=["RS256"], options={"verify_signature": False}
    )
    affinity = data["affinity"]
    if affinity not in CHAT_AFFINITY_DOMAINS:
        raise AffnityDomainNotFound(affinity)
    return CHAT_AFFINITY_DOMAINS[affinity]


def get_chat_host(pas_token: str):
    data = jwt.decode(  # type: ignore
        pas_token, algorithms=["RS256"], options={"verify_signature": False}
    )
    affinity = data["affinity"]
    if affinity not in CHAT_HOSTS:
        raise ChatHostNotFound(affinity)
    return CHAT_HOSTS[affinity]
