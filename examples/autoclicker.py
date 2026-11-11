# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper"]
# ///
from tapper import Tap
from tapper import send
from tapper import start
from tapper.helper import repeat

print("""Autoclicker (Windows only).

    F6      Starts clicking the left mouse button 20 times a second.
            Press again to stop.

    F3      Restarts.
    alt+F3  Quits.""")
start(Tap("f6", repeat.toggle(lambda: send("$(lmb)"), interval=0.05)))
