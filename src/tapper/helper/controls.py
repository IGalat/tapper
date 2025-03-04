import atexit
import os
import signal
import subprocess
import sys
import uuid

from tapper.controller import flow_control as _flow_control
from tapper.feedback.logger import log


def restart() -> None:
    log.info("Restarting tapper...")
    popen_args = [sys.executable] + sys.argv
    if sys.platform == "win32":
        subprocess.Popen(popen_args, creationflags=subprocess.DETACHED_PROCESS)
    else:
        subprocess.Popen(popen_args, start_new_session=True)
    _terminate()


def terminate() -> None:
    log.info("Terminating tapper...")
    _terminate()


def _terminate() -> None:
    atexit._run_exitfuncs()  # run all @atexit functions
    os.kill(os.getpid(), signal.SIGINT)


def pause_actions_on() -> None:
    """Puts actions (current and future) on pause, until turned off.
    Note: will only pause when `tapper.sleep` is used inside the action,
            directly or via other tapper functions."""
    log.debug("Pausing tapper actions")
    _flow_control.paused = True


def pause_actions_off() -> None:
    """Turns off pause. Does nothing if pause is already off."""
    log.debug("Un-pausing tapper actions")
    _flow_control.paused = False


def pause_actions_toggle() -> None:
    """Turns on pause if not paused, turns pause off if it's on."""
    log.debug(f"Pausing tapper actions toggle: {not _flow_control.paused}")
    _flow_control.paused = not _flow_control.paused


def kill_running_actions() -> None:
    """Kills currently running actions.
    Note: will only kill when `tapper.sleep` is used inside the action,
            directly or via other tapper functions."""
    log.debug("Killing tapper actions")
    _flow_control.kill_id = uuid.uuid4()
