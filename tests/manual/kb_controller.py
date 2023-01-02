import sys
import time

from manual.util_mantest import killme_in
from tapper.controller.keyboard import kb_api


def kb_commander() -> None:
    time.sleep(0.5)
    _, kbc = kb_api.by_os[sys.platform]()

    def click(symbol: str) -> bool:
        time.sleep(0.1)
        kbc.press(symbol)
        time.sleep(0.1)
        kbc.release(symbol)
        return True

    print("Move mouse cursor to the end of this py file.")
    time.sleep(1)

    [click(s) for s in "\n1q\\"]
    click("page_up")

    time.sleep(0.5)
    click("page_down")
    [click(s) for s in ["arrow_left", "backspace", "backspace", "backspace", "del"]]

    time.sleep(0.5)
    kbc.press("alt")
    click("tab")
    kbc.release("alt")

    time.sleep(0.5)
    kbc.press("alt")
    click("tab")
    kbc.release("alt")


def language_monitor() -> None:
    time.sleep(0.5)
    kbl, kbc = kb_api.by_os[sys.platform]()
    for _ in range(10):
        time.sleep(1)
        print(kbl.lang())

    kbc.set_lang("en")


def main() -> None:
    killme_in(11)
    language_monitor()


if __name__ == "__main__":
    main()
