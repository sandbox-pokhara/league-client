import os
import subprocess
import time

from .utils import is_running
from .utils import kill_process


def open_riot_client(path, headless=False):
    while not is_running('RiotClientServices.exe'):
        command = [path, '--launch-product=league_of_legends', '--launch-patchline=live']
        if headless:
            command.append('--headless')
        subprocess.Popen(command)
        time.sleep(1)


def open_league_client(path):
    while not is_running('LeagueClient.exe'):
        try:
            subprocess.Popen([path, '--headless'])
        except PermissionError:
            pass
        finally:
            time.sleep(1)


def kill_league_client():
    kill_process('LeagueClient.exe')
    kill_process('LeagueClientUx.exe')
    kill_process('LeagueClientUxRender.exe')
    kill_process('LeagueCrashHandler.exe')


def kill_riot_client():
    kill_process('RiotClientServices.exe')
    kill_process('RiotClientCrashHandler.exe')
    kill_process('RiotClientUx.exe')
    kill_process('RiotClientUxRender.exe')


def remove_lockfile(lockfile):
    try:
        os.remove(lockfile)
    except OSError:
        pass
