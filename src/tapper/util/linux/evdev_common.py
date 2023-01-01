from functools import cache

import evdev
from evdev import ecodes
from evdev import UInput
from evdev.eventio import EventIO


@cache
def get_real_keyboards() -> list[evdev.InputDevice]:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    result = []
    for d in devices:
        cap = d.capabilities()
        if ecodes.EV_KEY in cap:
            if ecodes.KEY_Q in cap[ecodes.EV_KEY]:
                result.append(d)
    if not result:
        raise PermissionError(
            "No keyboards detected."
            "You should run this as root, or "
            "if you don't need a keyboard listener and controller, "
            "remove them in tapper.config."
        )
    return result


def make_virtual_device_from(real_kbs: list[evdev.InputDevice], name: str) -> UInput:
    try:
        return UInput.from_device(*real_kbs, name="Tapper Virtual " + name)
    except evdev.UInputError:
        raise PermissionError("Cannot make virtual device. Try running as root.")


def uinput_action(device: EventIO, etype: int, code: int, evdev_direction: int) -> None:
    device.write(etype, code, evdev_direction)
    device.write(evdev.ecodes.EV_SYN, evdev.ecodes.SYN_REPORT, 0)


_virtual_keyboard: UInput | None = None


def get_virtual_kb() -> UInput:
    global _virtual_keyboard
    if not _virtual_keyboard:
        _virtual_keyboard = make_virtual_device_from(get_real_keyboards(), "Keyboard")
    return _virtual_keyboard
