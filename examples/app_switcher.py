# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper==2026.11.2"]
# ///
from functools import partial

from tapper import start
from tapper import window

print("""App switcher (Windows only). Open Chrome, VS Code and Telegram, then:

    ctrl+alt+1  Brings Chrome to the front.
    ctrl+alt+2  Brings VS Code to the front.
    ctrl+alt+3  Brings Telegram to the front.

    F3          Restarts.
    alt+F3      Quits.""")
start(
    {
        "ctrl+alt+1": partial(window.to_active, "chrome"),
        "ctrl+alt+2": partial(window.to_active, "code"),
        "ctrl+alt+3": partial(window.to_active, "telegram"),
    }
)
