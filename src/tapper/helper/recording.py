from functools import partial
from typing import Any
from typing import Callable

from tapper import send
from tapper.helper._util import record_util as _record_util
from tapper.helper.model import RecordConfig

last_recorded: str = ""


def _set_new_recording(new_recording: str) -> None:
    global last_recorded
    last_recorded = new_recording


def action_playback_last(speed: float = 1) -> partial:
    """For inserting in tap."""
    return partial(playback_last, speed=speed)


def playback_last(speed: float = 1) -> None:
    send(last_recorded, interval=0.05, speed=speed)


def start() -> Callable[[], None]:
    """
    Gives a function, that:
    Starts recording keystrokes and mouse clicks, and position of the mouse during these actions.
    If recording in progress, destroys it and starts a new one.

    :return: callable start, to be set into a Tap
    """
    return _record_util.start_recording


def stop(
    callback: Callable[[str], Any] = lambda s: None,
    config: RecordConfig = RecordConfig(),
) -> Callable[[], None]:
    """
    Gives a function, that:
    Stops recording, and if there was a recording, transforms recorded actions into a string
        that can be supplied to `send` and calls the callback with this string.

    :param callback: What to do with resulting string.
    :param config: config settings.
    :return: callable stop, to be set into a Tap.
    """
    return partial(_record_util.stop_recording, [_set_new_recording, callback], config)


def toggle(
    callback: Callable[[str], Any] = lambda s: None,
    config: RecordConfig = RecordConfig(),
) -> Callable[[], None]:
    """
    Gives a function, that:
    On first stroke, starts recording keystrokes and mouse clicks, and position of the mouse during these actions.
    On second stroke, stops recording, transforms recorded actions into a string that can be supplied to tapper.send
        and calls the callback with this string.

    :param callback: What to do with resulting string.
    :param config: config settings.
    :return: callable toggle, to be set into a Tap.
    """
    return partial(
        _record_util.toggle_recording, [_set_new_recording, callback], config
    )
