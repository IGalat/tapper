import os
import signal
import subprocess
import sys


def restart() -> None:
    print("Restarting tapper...")
    sys.stdout.flush()
    subprocess.Popen(
        [sys.executable] + sys.argv, creationflags=subprocess.DETACHED_PROCESS
    )
    _terminate()


def terminate() -> None:
    print("Terminating tapper...")
    _terminate()


def _terminate() -> None:
    os.kill(os.getpid(), signal.SIGINT)
