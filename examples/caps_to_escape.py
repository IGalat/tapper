# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper"]
# ///
# Caps Lock becomes Escape. Shift+Caps Lock still toggles caps.
from tapper import start

start({"caps": "esc", "shift+caps": "caps"})
