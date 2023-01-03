import os
from typing import Any

from tapper.helper import controls


def get_logo_path() -> str:
    return os.path.dirname(os.path.realpath(__file__)) + "/../resources/tapper_logo.jpg"


def make_menu() -> Any:
    from pystray import Menu, MenuItem

    return Menu(
        MenuItem("Restart", controls.restart), MenuItem("Exit", controls.terminate)
    )


def create() -> None:
    """Makes a visible tray icon."""
    try:
        import PIL.Image
        import pystray
    except ModuleNotFoundError:
        return

    logo = PIL.Image.open(get_logo_path())

    stray = pystray.Icon("tapper", logo, menu=make_menu())

    # this is blocking. Not running in separate thread for Mac compatibility
    # https://pystray.readthedocs.io/en/latest/usage.html
    stray.run()
