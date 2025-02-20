from functools import partial
from threading import Thread

import evdev
from evdev import UInput  # type: ignore
from tapper.model import constants
from tapper.model import keyboard
from tapper.model.constants import EvdevKeyDir
from tapper.model.constants import EvdevReverseKeyDir
from tapper.model.constants import KeyDirBool
from tapper.model.constants import ListenerResult
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener
from tapper.util.linux import evdev_common


def key_action(virtual_kb: UInput, code: int, evdev_direction: int) -> None:
    evdev_common.uinput_action(virtual_kb, evdev.ecodes.EV_KEY, code, evdev_direction)


class LinuxKeyboardSignalListener(KeyboardSignalListener):
    real_kbs: list[evdev.InputDevice]  # type: ignore
    virtual_kb: UInput

    @classmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        return keyboard.get_key_list(constants.OS.linux)

    def start(self) -> None:
        self.real_kbs = evdev_common.get_real_keyboards()
        self.virtual_kb = evdev_common.get_virtual_kb()
        for kb in self.real_kbs:
            Thread(target=partial(self.keyboard_loop, kb)).start()

    def stop(self) -> None:
        pass

    def keyboard_loop(self, kb: evdev.InputDevice) -> None:  # type: ignore
        for pressed_key_code in kb.active_keys():
            key_action(
                self.virtual_kb, pressed_key_code, EvdevReverseKeyDir[KeyDirBool.UP]
            )
        kb.grab()

        for event in kb.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                try:
                    symbol = keyboard.linux_evdev_code_to_symbol_map[event.code]
                    result_on = self.on_signal((symbol, EvdevKeyDir[event.value]))
                    if result_on == ListenerResult.PROPAGATE:
                        self.virtual_kb.write_event(event)
                except KeyError:
                    self.virtual_kb.write_event(event)
            else:
                self.virtual_kb.write_event(event)
