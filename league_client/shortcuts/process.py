import subprocess
import time

import psutil


def is_running(process_name: str):
    try:
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if process_name.lower() == proc.name().lower():
                    return True
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                pass
    except (TypeError, OSError):
        return False
    return False


def kill_process(process_name: str, retry_limit: int = 10):
    try:
        for _ in range(retry_limit):
            try:
                for proc in psutil.process_iter():
                    if proc.name().lower() == process_name.lower():
                        proc.kill()
                if not is_running(process_name):
                    return
            except (TypeError, OSError):
                pass
            time.sleep(1)
    except psutil.NoSuchProcess:
        return


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


def open_riot_client(path: str):
    while not is_running("RiotClientServices.exe"):
        try:
            subprocess.Popen([path])
        except PermissionError:
            pass
        finally:
            time.sleep(1)
