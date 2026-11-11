# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper[img]"]
# ///
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


print("""Click a button when it appears (Windows only).

    F2      Snips a button: press with the cursor on its top-left corner,
            then on its bottom-right corner. Saves ok_button.png.
    F4      Waits up to 10 seconds for the button to appear, then clicks it.

    F3      Restarts.
    alt+F3  Quits.""")
start(
    {
        "f2": img.snip(prefix="ok_button", bbox_to_name=False),
        "f4": click_ok_when_visible,
    }
)
