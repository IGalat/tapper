import os
import signal
import subprocess
import sys


def restart() -> None:
    print("Restarting tapper...")
    popen_args = [sys.executable] + sys.argv
    if sys.platform == "win32":
        subprocess.Popen(popen_args, creationflags=subprocess.DETACHED_PROCESS)
    else:
        subprocess.Popen(popen_args, start_new_session=True)
    _terminate()


def terminate() -> None:
    print("Terminating tapper...")
    _terminate()


def _terminate() -> None:
    os.kill(os.getpid(), signal.SIGINT)
