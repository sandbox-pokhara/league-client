import httpx

# parsed from
# https://clientconfig.rpg.riotgames.com/api/v1/config/player
# requires authorization
CHAT_AFFINITY_DOMAINS = {
    "as2": "as2",
    "asia": "jp1",
    "br1": "br1",
    "eu": "ru1",
    "eu3": "eu3",
    "eun1": "eu2",
    "euw1": "eu1",
    "jp1": "jp1",
    "kr1": "kr1",
    "la1": "la1",
    "la2": "la2",
    "na1": "na1",
    "oc1": "oc1",
    "pbe1": "pb1",
    "ru1": "ru1",
    "sea1": "sa1",
    "sea2": "sa2",
    "sea3": "sa3",
    "sea4": "sa4",
    "tr1": "tr1",
    "us": "la1",
    "us-br1": "br1",
    "us-la2": "la2",
    "us2": "us2",
}


# affinity to chat host mapping
# affinity is parsed from pas_token deserialization
CHAT_HOSTS = {
    "as2": "as2.chat.si.riotgames.com",
    "asia": "jp1.chat.si.riotgames.com",
    "br1": "br.chat.si.riotgames.com",
    "eu": "ru1.chat.si.riotgames.com",
    "eu3": "eu3.chat.si.riotgames.com",
    "eun1": "eun1.chat.si.riotgames.com",
    "euw1": "euw1.chat.si.riotgames.com",
    "jp1": "jp1.chat.si.riotgames.com",
    "kr1": "kr1.chat.si.riotgames.com",
    "la1": "la1.chat.si.riotgames.com",
    "la2": "la2.chat.si.riotgames.com",
    "na1": "na2.chat.si.riotgames.com",
    "oc1": "oc1.chat.si.riotgames.com",
    "pbe1": "pbe1.chat.si.riotgames.com",
    "ru1": "ru1.chat.si.riotgames.com",
    "sea1": "sa1.chat.si.riotgames.com",
    "sea2": "sa2.chat.si.riotgames.com",
    "sea3": "sa3.chat.si.riotgames.com",
    "sea4": "sa4.chat.si.riotgames.com",
    "tr1": "tr1.chat.si.riotgames.com",
    "us": "la1.chat.si.riotgames.com",
    "us-br1": "br.chat.si.riotgames.com",
    "us-la2": "la2.chat.si.riotgames.com",
    "us2": "us2.chat.si.riotgames.com",
}


CIPHERS = "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA:AES256-SHA:DES-CBC3-SHA"
ECDH_CURVE = "prime256v1"
SSL_CONTEXT = httpx.create_ssl_context()
SSL_CONTEXT.set_ciphers(CIPHERS)
SSL_CONTEXT.set_ecdh_curve(ECDH_CURVE)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X)"
        " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.1502.79 Mobile"
        " Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}


RIOT_CLIENT_AUTH_PARAMS = {
    "acr_values": "",
    "claims": "",
    "client_id": "riot-client",
    # commented because it returns 400 code
    # when using website authorize flow
    #
    # "code_challenge": "",
    # "code_challenge_method": "",
    "nonce": "SYXugqaAL5z7U7iioaTW5Q",
    "redirect_uri": "http://localhost/redirect",
    "response_type": "token id_token",
    "scope": "openid link ban lol_region account",
}

LEAGUE_CLIENT_AUTH_PARAMS = {
    "acr_values": "",
    "claims": "",
    "client_id": "lol",
    # commented because it returns 400 code
    # when using website authorize flow
    #
    # "code_challenge": "",
    # "code_challenge_method": "",
    "nonce": "SYXugqaAL5z7U7iioaTW5Q",
    "redirect_uri": "http://localhost/redirect",
    "response_type": "token id_token",
    "scope": "openid link ban lol_region lol summoner offline_access",
}

ACCOUNTODACTYL_PARAMS = {
    "scope": (
        "openid email profile riot://riot.atlas/accounts.edit"
        " riot://riot.atlas/accounts/password.edit"
        " riot://riot.atlas/accounts/email.edit"
        " riot://riot.atlas/accounts.auth riot://third_party.revoke"
        " riot://third_party.query riot://forgetme/notify.write"
        " riot://riot.authenticator/auth.code"
        " riot://riot.authenticator/authz.edit riot://rso/mfa/device.write"
        " riot://riot.authenticator/identity.add"
    ),
    "state": "fc5a8f17-e99f-4eb9-afd9-a950e0eb30c6",
    "acr_values": "urn:riot:gold",
    "ui_locales": "en",
    "client_id": "accountodactyl-prod",
    "redirect_uri": "https://account.riotgames.com/oauth2/log-in",
    "response_type": "code",
}


PROD_XSS0_RIOTGAMES = {
    "client_id": "prod-xsso-riotgames",
    "scope": "openid account email offline_access",
    "code_challenge_method": "S256",
    "code_challenge": "zUo5VZKlO9BvmC_KX5sihHLmeR7iy7sRoHO2WYxON58",
    "redirect_uri": "https://xsso.riotgames.com/redirect",
    "state": "9ef38e6acae290380703408405",
    "response_type": "code",
    "prompt": "login",
}
