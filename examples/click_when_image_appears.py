# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper[img]"]
# ///
# Windows only.
# 1. Hover the top-left corner of a button, press F2; hover its bottom-right corner, press F2.
#    That saves ok_button.png next to this script.
# 2. Press F4: tapper waits up to 10 seconds for the button to appear anywhere on screen, then clicks it.
from tapper import log
from tapper import mouse
from tapper import start
from tapper.helper import img


def click_ok_when_visible() -> None:
    found = img.wait_for("ok_button.png", timeout=10)
    if found is None:
        log.info("ok_button.png didn't appear")
        return
    x, y = found  # top-left corner of the match
    mouse.click(x + 5, y + 5)


start(
    {
        "f2": img.snip(prefix="ok_button", bbox_to_name=False),
        "f4": click_ok_when_visible,
    }
)
