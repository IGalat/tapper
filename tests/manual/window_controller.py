import sys
import time

from manual.util_mantest import killme_in
from tapper.boot import platforms
from tapper.controller.window.window_api import WindowController
from tapper.model.constants import Aspect


def window_controller() -> None:
    wc = WindowController()
    wc._init(platforms.for_os(sys.platform).drivers[Aspect.window]())
    wc._start()

    print("Open windows:")
    open_w = [w.__repr__() for w in wc.get_open()]
    print("\n".join(open_w))
    print(f"\nForeground window: {wc.active()}\n")

    win_name = input("Please enter name of open, non-maximized guinea pig app: ")
    wc.minimize(win_name)
    time.sleep(1)
    wc.restore(win_name)
    time.sleep(1)
    wc.maximize(win_name)
    time.sleep(1)
    wc.restore(win_name)
    time.sleep(1)
    wc.close(win_name)


def main() -> None:
    killme_in(30)
    window_controller()


if __name__ == "__main__":
    main()
