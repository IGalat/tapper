from functools import cache

import evdev
from evdev import UInput


@cache
def get_real_keyboards() -> list[evdev.InputDevice]:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    result = []
    for d in devices:
        cap = d.capabilities()
        if 1 in cap:  # EV_KEY
            if 16 in cap[1]:  # can type "q"
                result.append(d)
    if not result:
        raise PermissionError(
            "No keyboards detected."
            "You should run this as root, or "
            "if you don't need a keyboard signal listener, "
            "remove it in tapper.config."
        )
    return result


@cache
def get_real_mice() -> list[evdev.InputDevice]:
    pass


def make_virtual_device_from(real_kbs: list[evdev.InputDevice], name: str) -> UInput:
    try:
        return UInput.from_device(*real_kbs, name="Tapper Virtual " + name)
    except evdev.UInputError:
        raise PermissionError("Cannot make virtual device. Try running as root.")


def uinput_action(device: UInput, etype: int, code: int, evdev_direction: int) -> None:
    device.write(etype, code, evdev_direction)
    device.syn()


virtual_keyboard: UInput | None = None
virtual_mouse: UInput | None = None


def get_virtual_kb() -> UInput:
    global virtual_keyboard
    if not virtual_keyboard:
        virtual_keyboard = make_virtual_device_from(get_real_keyboards(), "Keyboard")
    return virtual_keyboard


def get_virtual_mouse_lazy() -> UInput:
    global virtual_mouse
    if not virtual_mouse:
        virtual_mouse = make_virtual_device_from(get_real_mice(), "Mouse")
    return virtual_mouse
