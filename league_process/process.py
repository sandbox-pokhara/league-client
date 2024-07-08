import os
import subprocess
import time

from league_process.utils import is_running
from league_process.utils import kill_process


def open_riot_client(path: str):
    while not is_running("RiotClientServices.exe"):
        try:
            subprocess.Popen([path])
        except PermissionError:
            pass
        finally:
            time.sleep(1)


def open_league_client(path: str):
    while not is_running("LeagueClient.exe"):
        try:
            subprocess.Popen([path])
        except PermissionError:
            pass
        finally:
            time.sleep(1)


def kill_league_client():
    kill_process("LeagueClient.exe")
    kill_process("LeagueClientUx.exe")
    kill_process("LeagueClientUxRender.exe")
    kill_process("LeagueCrashHandler.exe")


def kill_riot_client():
    kill_process("RiotClientServices.exe")
    kill_process("RiotClientCrashHandler.exe")
    kill_process("RiotClientUx.exe")
    kill_process("RiotClientUxRender.exe")


def remove_lockfile(lockfile: str):
    try:
        os.remove(lockfile)
    except OSError:
        pass
