# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper"]
# ///
# Windows only. Ctrl+Alt+1/2/3 bring an already-open app to the front.
from functools import partial

from tapper import start
from tapper import window

start(
    {
        "ctrl+alt+1": partial(window.to_active, "chrome"),
        "ctrl+alt+2": partial(window.to_active, "code"),
        "ctrl+alt+3": partial(window.to_active, "telegram"),
    }
)
