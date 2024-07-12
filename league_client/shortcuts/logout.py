import os

from league_client.shortcuts import logger
from league_client.shortcuts.process import kill_league_client
from league_client.shortcuts.process import kill_riot_client


def remove_riot_private_settings():
    logger.info("Removing riot private settings...")
    path = os.path.expandvars(
        r"%LOCALAPPDATA%\Riot Games\Riot"
        r" Client\Data\RiotGamesPrivateSettings.yaml"
    )
    try:
        os.remove(path)
    except OSError:
        pass


def logout(league_lockfile: str):
    logger.info("Logging out...")
    kill_league_client()
    kill_riot_client()
    try:
        os.remove(league_lockfile)
    except OSError:
        pass
