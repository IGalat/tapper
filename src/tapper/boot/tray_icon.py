import os
from typing import Any

from tapper.feedback.logger import log
from tapper.helper import controls

_icon: Any = None


def get_logo_path() -> str:
    return os.path.dirname(os.path.realpath(__file__)) + "/../resources/tapper_logo.jpg"


def make_menu() -> Any:
    from pystray import Menu
    from pystray import MenuItem

    return Menu(
        MenuItem("Restart", controls.restart), MenuItem("Exit", controls.terminate)
    )


def create() -> None:
    """Makes a visible tray icon."""
    global _icon
    try:
        import PIL.Image
        import pystray
    except ModuleNotFoundError:
        return

    log.debug("Creating tray icon")

    logo = PIL.Image.open(get_logo_path())

    _icon = pystray.Icon("tapper", logo, menu=make_menu())
    _icon.run_detached()


def remove() -> None:
    if _icon is not None:
        _icon.stop()
