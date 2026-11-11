# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper==2026.11.1"]
# ///
from tapper import start

print("""Caps Lock as Escape.

    caps        Presses Escape.
    shift+caps  Toggles Caps Lock.

    F3          Restarts.
    alt+F3      Quits.""")
start({"caps": "esc", "shift+caps": "caps"})
