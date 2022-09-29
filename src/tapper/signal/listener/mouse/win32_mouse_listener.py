from typing import Final

import winput
from tapper.signal.listener.mouse.mouse_listener import MouseSignalListener
from winput import MouseEvent

WINPUT_PROPAGATE: Final[int] = 0
WINPUT_SUPPRESS: Final[int] = 4


def to_callback_result(inner_func_result: bool) -> int:
    if inner_func_result:
        return WINPUT_PROPAGATE
    else:
        return WINPUT_SUPPRESS


class Win32MouseSignalListener(MouseSignalListener):
    def start(self) -> None:
        winput.set_DPI_aware(True)
        winput.hook_mouse(self.mouse_callback)
        winput.wait_messages()

    def stop(self) -> None:
        winput.stop()
        winput.unhook_mouse()

    def mouse_callback(self, event: MouseEvent) -> int:
        return to_callback_result(self._mouse_callback(event))

    def _mouse_callback(self, event: MouseEvent) -> bool:
        action = event.action

        if action == 512:  # mouse move
            return True

        elif action == 522:
            if event.additional_data > 0:
                return self.on_signal(("scroll_wheel_up", True))
            else:
                return self.on_signal(("scroll_wheel_down", True))

        elif action == 513:
            return self.on_signal(("left_mouse_button", True))
        elif action == 514:
            return self.on_signal(("left_mouse_button", False))

        elif action == 516:
            return self.on_signal(("right_mouse_button", True))
        elif action == 517:
            return self.on_signal(("right_mouse_button", False))

        elif action == 519:
            return self.on_signal(("middle_mouse_button", True))
        elif action == 520:
            return self.on_signal(("middle_mouse_button", False))

        elif action == 523 and event.additional_data == 1:
            return self.on_signal(("x1_mouse_button", True))
        elif action == 524 and event.additional_data == 1:
            return self.on_signal(("x1_mouse_button", False))

        elif action == 523 and event.additional_data == 2:
            return self.on_signal(("x2_mouse_button", True))
        elif action == 524 and event.additional_data == 2:
            return self.on_signal(("x2_mouse_button", False))
        else:
            return True
