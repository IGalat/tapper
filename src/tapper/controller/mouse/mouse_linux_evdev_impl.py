from typing import Optional

import evdev
from evdev import UInput
from tapper.controller.mouse.mouse_api import calc_move
from tapper.controller.mouse.mouse_api import MouseCommander
from tapper.controller.mouse.mouse_api import MouseTracker
from tapper.model import mouse
from tapper.model.constants import EvdevReverseKeyDir
from tapper.model.constants import KeyDirBool
from tapper.util import datastructs
from tapper.util.linux import evdev_common

mouse_buttons_w_aliases = {
    **mouse.button_aliases,
    **{b: [b] for b in mouse.regular_buttons},
}

symbol_button_map = datastructs.symbols_to_codes(
    mouse.linux_evdev_code_button_map, mouse_buttons_w_aliases  # type: ignore
)

wheel_w_aliases = {**mouse.wheel_aliases, **{b: [b] for b in mouse.wheel_buttons}}

wheel_w_aliases = {
    k: v
    for k, v in wheel_w_aliases.items()
    if v[0] not in ["scroll_wheel_left", "scroll_wheel_right"]
}

symbol_wheel_map = datastructs.symbols_to_codes(
    mouse.linux_evdev_code_wheel_map, wheel_w_aliases  # type: ignore
)


def extract_coords(m: evdev.InputDevice) -> tuple[int, int] | None:
    cap = m.capabilities()
    if evdev.ecodes.EV_ABS not in cap or len(cap[evdev.ecodes.EV_ABS]) < 2:
        return None
    x, y = None, None
    for pos_tuple in cap[evdev.ecodes.EV_ABS]:
        if pos_tuple[0] == evdev.ecodes.ABS_X:
            x = pos_tuple[1].value
        elif pos_tuple[0] == evdev.ecodes.ABS_Y:
            y = pos_tuple[1].value
    if x is None and y is None:
        return None
    return x, y


class LinuxMouseTrackerCommander(MouseTracker, MouseCommander):
    real_mice: list[evdev.InputDevice]
    virtual_mouse: UInput

    def start(self) -> None:
        self.real_mice = evdev_common.get_real_mice()
        self.virtual_mouse = evdev_common.get_virtual_mouse()

    def stop(self) -> None:
        pass

    def press(self, symbol: str) -> None:
        try:
            evdev_common.uinput_action(
                self.virtual_mouse,
                evdev.ecodes.EV_KEY,
                symbol_button_map[symbol][0],
                EvdevReverseKeyDir[KeyDirBool.DOWN],
            )
        except KeyError:
            code, value = symbol_wheel_map[symbol][0]
            evdev_common.uinput_action(
                self.virtual_mouse, evdev.ecodes.EV_REL, code, value
            )

    def release(self, symbol: str) -> None:
        try:
            evdev_common.uinput_action(
                self.virtual_mouse,
                evdev.ecodes.EV_KEY,
                symbol_button_map[symbol][0],
                EvdevReverseKeyDir[KeyDirBool.UP],
            )
        except KeyError:
            if symbol not in symbol_wheel_map:
                raise KeyError

    def move(
        self, x: Optional[int] = None, y: Optional[int] = None, relative: bool = False
    ) -> None:
        new_x, new_y = calc_move(self.get_pos, x, y, relative)
        self.virtual_mouse.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_X, new_x)
        self.virtual_mouse.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_Y, new_y)
        self.virtual_mouse.syn()

    def get_pos(self) -> tuple[int, int]:
        coords = next(extract_coords(m) for m in self.real_mice)
        return coords or (0, 0)

    def pressed(self, symbol: str) -> bool:
        try:
            code = symbol_button_map[symbol]
            for m in self.real_mice:
                mpress = m.active_keys()
                print(mpress)
                if code[0] in mpress:
                    return True
            return False
        except KeyError:
            return False

    def toggled(self, symbol: str) -> bool:
        return False
