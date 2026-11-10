import runpy
import sys
import time

from tapper import send
from tapper import start

DEMO_INTRO = """tapper demo. Go to any text field, then:

    F8      Types a greeting.
    F9      Types the current time.
    F10     Moves the mouse around.

    F3      Restarts.
    alt+F3  Quits.

To run your own scripts: tapper my_scripts.py"""


def main() -> None:
    if len(sys.argv) > 1:
        # Drop own name, so the script sees args and controls.restart reruns it.
        sys.argv = sys.argv[1:]
        runpy.run_path(sys.argv[0], run_name="__main__")
        return

    print(DEMO_INTRO)  # noqa: T201  # logging only starts inside start()
    start(
        {
            "f8": "Hello from tapper!",
            "f9": lambda: send(time.strftime("%H:%M")),
            "f10": "$(x200y0r;.3s;x0y200r;.3s;x-200y0r;.3s;x0y-200r)",
        }
    )


if __name__ == "__main__":
    main()
