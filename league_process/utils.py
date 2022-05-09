import time

import psutil


def is_running(process_name):
    try:
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if process_name.lower() == proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except (TypeError, OSError):
        return False
    return False


def kill_process(process_name, retry_limit=10):
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
