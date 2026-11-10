# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper"]
# ///
# Windows only. F6 starts clicking the left mouse button 20 times a second, F6 again stops.
from tapper import Tap
from tapper import send
from tapper import start
from tapper.helper import repeat

start(Tap("f6", repeat.toggle(lambda: send("$(lmb)"), interval=0.05)))
