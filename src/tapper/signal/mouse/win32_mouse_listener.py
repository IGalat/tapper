from threading import Thread

import winput
from tapper.feedback.logger import LogExceptions
from tapper.model.constants import KeyDirBool
from tapper.model.constants import ListenerResult
from tapper.model.constants import WinputListenerResult
from tapper.signal.mouse.mouse_listener import MouseSignalListener
from winput import MouseEvent


class Win32MouseSignalListener(MouseSignalListener):
    def start(self) -> None:
        Thread(target=self.event_loop_start).start()

    @LogExceptions()
    def event_loop_start(self) -> None:
        winput.set_DPI_aware(per_monitor=True)
        winput.hook_mouse(self.mouse_callback)
        winput.wait_messages()

    @LogExceptions()
    def stop(self) -> None:
        winput.stop()
        winput.unhook_mouse()

    @LogExceptions()
    def mouse_callback(self, event: MouseEvent) -> int:
        return WinputListenerResult[self._mouse_callback(event)]

    def _mouse_callback(self, event: MouseEvent) -> ListenerResult:
        action = event.action

        if action == 512:  # mouse move
            return ListenerResult.PROPAGATE

        elif action == 522:
            if event.additional_data > 0:
                return self.on_signal(("scroll_wheel_up", KeyDirBool.DOWN))
            else:
                return self.on_signal(("scroll_wheel_down", KeyDirBool.DOWN))

        elif action == 513:
            return self.on_signal(("left_mouse_button", KeyDirBool.DOWN))
        elif action == 514:
            return self.on_signal(("left_mouse_button", KeyDirBool.UP))

        elif action == 516:
            return self.on_signal(("right_mouse_button", KeyDirBool.DOWN))
        elif action == 517:
            return self.on_signal(("right_mouse_button", KeyDirBool.UP))

        elif action == 519:
            return self.on_signal(("middle_mouse_button", KeyDirBool.DOWN))
        elif action == 520:
            return self.on_signal(("middle_mouse_button", KeyDirBool.UP))

        elif action == 523 and event.additional_data == 1:
            return self.on_signal(("x1_mouse_button", KeyDirBool.DOWN))
        elif action == 524 and event.additional_data == 1:
            return self.on_signal(("x1_mouse_button", KeyDirBool.UP))

        elif action == 523 and event.additional_data == 2:
            return self.on_signal(("x2_mouse_button", KeyDirBool.DOWN))
        elif action == 524 and event.additional_data == 2:
            return self.on_signal(("x2_mouse_button", KeyDirBool.UP))
        else:
            return ListenerResult.PROPAGATE
