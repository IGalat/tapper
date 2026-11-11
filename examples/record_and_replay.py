# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper==2026.11.1"]
# ///
from tapper import log
from tapper import start
from tapper.helper import recording

print("""Record and replay (Windows only).

    F7      Starts recording keys and clicks. Press again to stop: the recording
            is logged as a string you can paste into send() to keep it.
    F8      Replays the last recording at double speed.

    F3      Restarts.
    alt+F3  Quits.""")
start(
    {
        "f7": recording.toggle(log.info),
        "f8": recording.action_playback_last(speed=2),
    }
)
