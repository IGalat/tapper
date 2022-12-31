import time
from functools import partial
from threading import Thread

import evdev
from evdev import InputEvent
from evdev import UInput
from tapper.model import constants
from tapper.model import keyboard
from tapper.model.constants import EvdevKeyDir
from tapper.model.constants import KeyDirBool
from tapper.model.constants import ListenerResult
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener


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


def make_virtual_kb_from(real_kb: evdev.InputDevice) -> UInput:
    try:
        return UInput.from_device(real_kb, name="Tapper-listener Virtual Keyboard")
    except evdev.UInputError:
        raise PermissionError("Cannot make virtual keyboard. Try running as root.")


def key_action(virtual_kb: UInput, code: int, evdev_direction: int) -> None:
    virtual_kb.write(evdev.ecodes.EV_KEY, code, evdev_direction)
    virtual_kb.syn()
    if EvdevKeyDir[evdev_direction] == KeyDirBool.UP:
        time.sleep(0.001)  # else lock fails to be acquired sometimes.


class LinuxKeyboardSignalListener(KeyboardSignalListener):
    real_kbs: list[evdev.InputDevice]
    virtual_kb: UInput

    @classmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        return keyboard.get_key_list(constants.OS.linux)

    def start(self) -> None:
        self.real_kbs = get_real_keyboards()
        self.virtual_kb = make_virtual_kb_from(self.real_kbs[0])
        for kb in self.real_kbs:
            Thread(target=partial(self.keyboard_loop, kb)).start()

    def stop(self) -> None:
        pass

    def keyboard_loop(self, kb: evdev.InputDevice) -> None:
        for pressed_key_code in kb.active_keys():
            key_action(self.virtual_kb, pressed_key_code, 0)  # lift
        kb.grab()

        for event in kb.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                try:
                    symbol = keyboard.linux_evdev_code_to_symbol_map[event.code]
                    result_on = self.on_signal((symbol, EvdevKeyDir[event.value]))
                    if result_on == ListenerResult.PROPAGATE:
                        self.propagate(event)
                except KeyError:
                    self.propagate(event)

    def propagate(self, event: InputEvent) -> None:
        key_action(self.virtual_kb, event.code, event.value)
