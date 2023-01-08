from manual.util_mantest import killme_in
from tapper import Group
from tapper import mouse
from tapper import root
from tapper import send
from tapper import start
from tapper import Tap
from tapper import window


def duplicate_chrome_tab() -> None:
    send("$(rmb)")
    pos = mouse.get_pos()
    mouse.move(55, 142, relative=True)
    send("$(lmb)")
    mouse.move(*pos)


def tapper_simple() -> None:
    root.add(
        Group("simple_actions_no_conditions").add(
            {
                "q": "qwerty",
                "\\": "Hello $(1s)there!",
                "shift 1s+]": "Any ",
                "lmb+arrow_right up 1s": "mainTime",
                "mmb": lambda: send("middle", interval=0.2),
                "f1": "$(x10y10)",
                "ctrl+f1": lambda: send("$(ctrl up)1s $(10s)delay", speed=10),
                "f6": "lmb",
            }
        ),
        Group("remap").add(
            {
                "apps": "_",
                "apps up": "",
                "print_screen": "$(insert)",
                "shift+print_screen": "$(ctrl+v)",
                "insert": "$(print_screen)",
            }
        ),
        Group(win_exec="chrome.exe").add(
            {
                "alt+\\": lambda: mouse.move(20, 20),
                "ctrl+d": duplicate_chrome_tab,
            }
        ),
        Tap("num9", window.close),
    )
    start()


def main() -> None:
    killme_in(120)
    tapper_simple()


if __name__ == "__main__":
    main()
