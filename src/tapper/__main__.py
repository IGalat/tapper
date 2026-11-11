import runpy
import sys
import time

import tapper
from tapper import Tap
from tapper import send
from tapper import start


def move_in_square() -> None:
    # Absolute moves: Windows applies pointer acceleration to relative ones, distorting the square.
    x, y = tapper.mouse.get_pos()
    send(f"$(x{x + 200}y{y};.3s;x{x + 200}y{y + 200};.3s;x{x}y{y + 200};.3s;x{x}y{y})")


def main() -> None:
    if len(sys.argv) > 1:
        # Drop own name, so the script sees args and controls.restart reruns it.
        sys.argv = sys.argv[1:]
        runpy.run_path(sys.argv[0], run_name="__main__")
        return

    print(  # noqa: T201  # logging only starts inside start()
        """Welcome!
This is tapper demo. Try these hotkeys:

    F10     Moves the mouse in a square.
    F11     Only in chrome - opens new tab. Works normally in other apps.

    Go to any text field, such as notepad, then:

    F8      Types a greeting.
    F9      Types the current time.

    F3      Restarts.
    alt+F3  Quits.

To run your own scripts: tapper my_scripts.py"""
    )

    start(
        {
            "f8": "Hello from tapper!",
            "f9": lambda: send("Current time is " + time.strftime("%H:%M")),
            "f10": move_in_square,
        },
        Tap("f11", "$(ctrl+t)", win_exec="chrome.exe"),
    )


if __name__ == "__main__":
    main()
