import random
import time

from tapper import Group
from tapper import kb
from tapper import root
from tapper import send
from tapper import start
from tapper import Tap
from tapper.helper import actions

recording: str = ""


def set_recording(new_recording: str) -> None:
    global recording
    recording = new_recording


def helpers() -> None:
    root.add(
        Group("repeat").add(
            {
                "[": actions.repeat_while(
                    lambda: random.randint(0, 2), lambda: print("randint")
                ),
                "]": actions.repeat_while(
                    lambda: kb.pressed("ctrl"), lambda: print("ctrl!"), 0.5
                ),
                "p": actions.repeat_while_pressed(
                    "p", lambda: print(f"{time.time():.3f}")
                ),
                "o": actions.repeat_while_pressed("o", lambda: print("o", end=""), 1),
            },
            Tap("(", actions.toggle_repeat(lambda: print("Sadge"), 1, 4)),
            Tap(")", actions.toggle_repeat(lambda: print("sMILE"), 1, 4)),
        ),
        Group("recording").add(
            {
                "numpad_minus": actions.record_toggle(set_recording),
                "ctrl+numpad_minus": actions.record_start(),
                "numpad_plus": lambda: send(recording, interval=0.1, speed=2),
                "ctrl+numpad_plus": lambda: print(recording),
            },
        ),
    )
    start()


def main() -> None:
    helpers()


if __name__ == "__main__":
    main()
