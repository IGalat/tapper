import sys
import time

import evdev
from evdev import UInput
from tapper.controller.keyboard.kb_api import KeyboardCommander
from tapper.controller.keyboard.kb_api import KeyboardTracker
from tapper.model import keyboard
from tapper.model.constants import EvdevReverseKeyDir
from tapper.model.constants import KeyDirBool
from tapper.util import datastructs
from tapper.util.linux import evdev_common

keys_wo_upper = {
    k: v
    for k, v in keyboard.get_keys(sys.platform).items()
    if k not in keyboard.chars_en_upper
}

symbol_code_map = datastructs.symbols_to_codes(
    keyboard.linux_evdev_code_to_symbol_map, keys_wo_upper  # type: ignore
)

modifier_led_indices = {"caps": 1, "caps_lock": 1, "num_lock": 0, "scroll_lock": 2}


class LinuxKeyboardTrackerCommander(KeyboardTracker, KeyboardCommander):
    real_kbs: list[evdev.InputDevice]
    virtual_kb: UInput

    def start(self) -> None:
        self.real_kbs = evdev_common.get_real_keyboards()
        self.virtual_kb = evdev_common.get_virtual_kb()

    def stop(self) -> None:
        pass

    def press(self, symbol: str) -> None:
        evdev_common.uinput_action(
            self.virtual_kb,
            evdev.ecodes.EV_KEY,
            symbol_code_map[symbol][0],  # type: ignore
            EvdevReverseKeyDir[KeyDirBool.DOWN],
        )
        time.sleep(0.001)  # else evdev-lib lock fails to be acquired sometimes.

    def release(self, symbol: str) -> None:
        evdev_common.uinput_action(
            self.virtual_kb,
            evdev.ecodes.EV_KEY,
            symbol_code_map[symbol][0],  # type: ignore
            EvdevReverseKeyDir[KeyDirBool.UP],
        )

    def pressed(self, symbol: str) -> bool:
        code = symbol_code_map[symbol]
        return any(code in kb.active_keys() for kb in self.real_kbs)

    def toggled(self, symbol: str) -> bool:
        """Limited to modifier keys."""
        led_index = modifier_led_indices.get(symbol, -1)
        if led_index == -1:
            return False
        return any(led_index in kb.leds() for kb in self.real_kbs)
