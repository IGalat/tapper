# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper"]
# ///
# Windows only. F7 starts recording keys and clicks, F7 again stops and logs a send-able string.
# F8 replays the last recording at double speed; paste the logged string into send() to keep it.
from tapper import log
from tapper import start
from tapper.helper import recording

start(
    {
        "f7": recording.toggle(log.info),
        "f8": recording.action_playback_last(speed=2),
    }
)
