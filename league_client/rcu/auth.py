from league_client.connection import LeagueConnection


def get_rq_data_and_site_key(riot_connection: LeagueConnection):
    riot_connection.delete("/rso-authenticator/v1/authentication")
    res = riot_connection.post(
        "/rso-authenticator/v1/authentication/riot-identity/start",
        json={
            "language": "en_GB",
            "productId": "riot-client",
            "state": "auth",
        },
    )
    res.raise_for_status()
    return res.json()["captcha"]["hcaptcha"]


def get_is_authorized(riot_connection: LeagueConnection):
    res = riot_connection.get("/rso-auth/v1/authorization")
    return res.status_code != 400


def get_is_agreement_required(riot_connection: LeagueConnection):
    res = riot_connection.get("/eula/v1/agreement")
    if res.status_code == 404:
        return False
    res = res.json()
    if "acceptance" not in res:
        return False
    return res["acceptance"] not in ["Accepted", "WaitingForAllServiceData"]


def get_is_age_restricted(riot_connection: LeagueConnection) -> bool:
    response = riot_connection.get(
        "/age-restriction/v1/age-restriction/products/league_of_legends"
    )
    response = response.json()
    return response.get("restricted", False)


def get_is_country_region_missing(riot_connection: LeagueConnection) -> bool:
    response = riot_connection.get("/riot-client-auth/v1/userinfo")
    response = response.json()
    return response.get("country", "npl") == "nan"


def accept_agreement(riot_connection: LeagueConnection):
    riot_connection.put("/eula/v1/agreement/acceptance")
