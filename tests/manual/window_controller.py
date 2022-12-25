import sys
import time

from tapper.controller.window.window_api import WindowController


def window_controller() -> None:
    wc = WindowController()
    wc._only_visible_windows = True
    wc._os = sys.platform
    wc._init()
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
    window_controller()


if __name__ == "__main__":
    main()
