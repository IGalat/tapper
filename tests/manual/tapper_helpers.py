import random
import time

from manual.util_mantest import killme_in
from tapper import Group
from tapper import kb
from tapper import root
from tapper import start
from tapper import Tap
from tapper.helper import img
from tapper.helper import recording
from tapper.helper import repeat


def print_pixel(color: tuple[int, int, int], coords: tuple[int, int]) -> None:
    int_to_hex_str = lambda int_: ("0" + repr(hex(int_))[3:-1].upper())[-2:]
    color_hex = (
        int_to_hex_str(color[0]) + int_to_hex_str(color[1]) + int_to_hex_str(color[2])
    )
    print(f"Pixel {color = } {color_hex=} at {coords = }")


def helpers() -> None:
    root.add(
        Group("repeat").add(
            {
                "[": repeat.while_fn(
                    lambda: random.randint(0, 2), lambda: print("randint")
                ),
                "]": repeat.while_fn(
                    lambda: kb.pressed("ctrl"), lambda: print("ctrl!"), 0.5
                ),
                "p": repeat.while_pressed("p", lambda: print(f"{time.time():.3f}")),
                "o": repeat.while_pressed("o", lambda: print("o", end=""), 1),
            },
            Tap("(", repeat.toggle(lambda: print("Sadge"), 1, 4)),
            Tap(")", repeat.toggle(lambda: print("sMILE"), 1, 4)),
        ),
        Group("recording").add(
            {
                "numpad_minus": recording.toggle(),
                "ctrl+numpad_minus": recording.start(),
                "numpad_plus": recording.action_playback_last(speed=2),
                "ctrl+numpad_plus": lambda: print(recording.last_recorded),
            },
        ),
        Group("img").add(
            {
                "num1": lambda: print(
                    img.find("small_test_img.png", (500, -1080, 600, -900))
                ),  # open this pic when testing
                "num2": img.snip(),
                "num3": lambda: print(
                    img.wait_for("snip_test-(BBOX_6_-1043_103_-1017).png")
                ),
                "num4": img.pixel_info(callback_for_data=print_pixel),
                "num5": img.pixel_info(print),
                "num6": lambda: print(img.pixel_find((62, 134, 160), (39, 43))),
            }
        ),
    )
    start()


def main() -> None:
    killme_in(120)
    helpers()


if __name__ == "__main__":
    main()
