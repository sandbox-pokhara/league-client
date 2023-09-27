import os

from league_process.process import kill_league_client
from league_process.process import kill_riot_client
from league_process.process import remove_lockfile

from .logger import logger


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


def logout_session(connection):
    logger.info("Deleting session...")
    return connection.delete("/rso-auth/v1/session")


def logout(league_lockfile):
    logger.info("Logging out...")
    kill_league_client()
    kill_riot_client()
    remove_lockfile(league_lockfile)
