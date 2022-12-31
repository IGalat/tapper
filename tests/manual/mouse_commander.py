import sys
import time

from manual.util_mantest import killme_in
from tapper.controller.mouse.mouse_api import MouseController
from tapper.state import keeper


# Had to use controller here, need get_pos
def mouse_commander() -> None:
    mc = MouseController()
    mc._emul_keeper = keeper.Emul()
    mc._os = sys.platform
    mc._init()
    mc._start()
    time.sleep(0.5)

    def click(symbol: str) -> None:
        time.sleep(0.1)
        mc.press(symbol)
        time.sleep(0.1)
        mc.release(symbol)
        time.sleep(0.1)

    print("Position the cursor at the mouse_commander method name.")
    time.sleep(2)

    pos = mc.get_pos()
    [click("lmb") for _ in range(3)]
    print("Now the line is selected.")
    time.sleep(2)

    mc.move(y=400, relative=True)
    mc.press("lmb")
    time.sleep(0.1)
    mc.move(y=-400, x=5, relative=True)
    print("Now some lines below are selected too.")
    time.sleep(2)

    mc.release("lmb")
    click("lmb")
    print("Now nothing is selected.")
    time.sleep(2)

    click("rmb")
    print("Now context menu is open.")
    time.sleep(2)

    mc.move(*pos)
    click("mmb")
    print("Now middle mouse action is performed on method name: in IDEA, goto usage.")
    time.sleep(2)

    screen_size = (1920, 1080)
    mc.move(x=screen_size[0] // 2, y=screen_size[1] // 2)
    print(
        "Now mouse cursor should be in the middle of your screen (make sure screen_size matches)."
    )


def main() -> None:
    killme_in(15)
    mouse_commander()


if __name__ == "__main__":
    main()
