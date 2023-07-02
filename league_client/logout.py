from league_process.process import kill_league_client
from league_process.process import kill_riot_client
from league_process.process import remove_lockfile

from .logger import logger


def logout(league_lockfile):
    logger.info("Logging out...")
    kill_league_client()
    kill_riot_client()
    remove_lockfile(league_lockfile)
