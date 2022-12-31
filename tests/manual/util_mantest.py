import os
import signal
import time
from functools import partial
from threading import Thread


def _killme(timeout: int) -> None:
    time.sleep(timeout)
    os.kill(os.getpid(), signal.SIGINT)


def killme_in(timeout: int) -> None:
    Thread(target=partial(_killme, timeout)).start()
