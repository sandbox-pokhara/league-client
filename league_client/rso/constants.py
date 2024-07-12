# KR, PBE, TW2 is not supported yet
# example: euc1-green.pp.sgp.pvp.net
# can be found in C:\Riot Games\League of Legends\system.yaml
# in player_platform_edge_url field
from enum import Enum

PLAYER_PLATFORM_EDGE_URL = {
    "EUW1": "https://euc1-red.pp.sgp.pvp.net",
    "EUN1": "https://euc1-red.pp.sgp.pvp.net",
    "NA1": "https://usw2-red.pp.sgp.pvp.net",
    "LA1": "https://usw2-red.pp.sgp.pvp.net",
    "LA2": "https://usw2-red.pp.sgp.pvp.net",
    "TR1": "https://euc1-red.pp.sgp.pvp.net",
    "RU": "https://euc1-red.pp.sgp.pvp.net",
    "OC1": "https://apse1-red.pp.sgp.pvp.net",
    "BR1": "https://usw2-red.pp.sgp.pvp.net",
    "JP1": "https://apne1-red.pp.sgp.pvp.net",
    "SG2": "https://apse1-red.pp.sgp.pvp.net",
    "PH2": "https://apse1-red.pp.sgp.pvp.net",
    "VN2": "https://apse1-red.pp.sgp.pvp.net",
    "TH2": "https://apse1-red.pp.sgp.pvp.net",
}

# KR, PBE, TW2 is not supported yet
# example: br-red.lol.sgp.pvp.net
# can be found in C:\Riot Games\League of Legends\system.yaml
# in league_edge_url field
LEAGUE_EDGE_URL = {
    "BR1": "https://br-red.lol.sgp.pvp.net",
    "EUN1": "https://eune-red.lol.sgp.pvp.net",
    "EUW1": "https://euw-red.lol.sgp.pvp.net",
    "JP1": "https://jp-red.lol.sgp.pvp.net",
    "LA1": "https://lan-red.lol.sgp.pvp.net",
    "LA2": "https://las-red.lol.sgp.pvp.net",
    "NA1": "https://na-red.lol.sgp.pvp.net",
    "OC1": "https://oce-red.lol.sgp.pvp.net",
    "RU": "https://ru-red.lol.sgp.pvp.net",
    "TR1": "https://tr-red.lol.sgp.pvp.net",
    "SG2": "https://sg2-red.lol.sgp.pvp.net",
    "PH2": "https://ph2-red.lol.sgp.pvp.net",
    "VN2": "https://vn2-red.lol.sgp.pvp.net",
    "TH2": "https://th2-red.lol.sgp.pvp.net",
}

# KR, PBE, TW2 is not supported yet
# example: lolriot.aws-euc1-prod.euw1
# can be found in C:\Riot Games\League of Legends\system.yaml
# in discoverous_service_location field
DISCOVEROUS_SERVICE_LOCATION = {
    "BR1": "lolriot.aws-usw2-prod.br1",
    "EUN1": "lolriot.aws-euc1-prod.eun1",
    "EUW1": "lolriot.aws-euc1-prod.euw1",
    "JP1": "lolriot.aws-apne1-prod.jp1",
    "LA1": "lolriot.aws-usw2-prod.la1",
    "LA2": "lolriot.aws-usw2-prod.la2",
    "NA1": "lolriot.aws-usw2-prod.na1",
    "OC1": "lolriot.aws-apse1-prod.oc1",
    "RU": "lolriot.aws-euc1-prod.ru",
    "TR1": "lolriot.aws-euc1-prod.tr1",
    "SG2": "lolriot.aws-euc1-prod.sg2",
    "PH2": "lolriot.aws-euc1-prod.ph2",
    "VN2": "lolriot.aws-euc1-prod.vn2",
    "TH2": "lolriot.aws-euc1-prod.th2",
}


class InventoryTypes(str, Enum):
    champion = "CHAMPION"
    champion_skin = "CHAMPION_SKIN"
    event_pass = "EVENT_PASS"
    skin_augment = "SKIN_AUGMENT"
    skin_border = "SKIN_BORDER"
    queue_entry = "QUEUE_ENTRY"


class LootNameTypes(str, Enum):
    key_fragment = "MATERIAL_key_fragment"
    key = "MATERIAL_key"
    generic_chest = "CHEST_generic"
    champion_mastery_chest = "CHEST_champion_mastery"
    masterwork_chest = "CHEST_224"
    blue_essence = "CURRENCY_champion"
    orange_essence = "CURRENCY_cosmetic"
    mythic_essence = "CURRENCY_mythic"
    chest_new_player = "CHEST_new_player"
    chest_day_one = "CHEST_day_one"
