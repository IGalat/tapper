from typing import Callable

from tapper.controller.flow_control import config_thread_local_storage
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.model import constants
from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.errors import SendError
from tapper.model.send import CursorMoveInstruction
from tapper.model.send import KeyInstruction
from tapper.model.send import SendInstruction
from tapper.model.send import SleepInstruction
from tapper.model.send import WheelInstruction
from tapper.parser.send_parser import SendParser


class SendCommandProcessor:
    """Highest-level component for "send" command."""

    os: str
    parser: SendParser
    kb_controller: KeyboardController
    mouse_controller: MouseController
    sleep_fn: Callable[[float], None]

    def __init__(
        self,
        os: str,
        parser: SendParser,
        kb_controller: KeyboardController,
        mouse_controller: MouseController,
        sleep_fn: Callable[[float], None],
    ) -> None:
        self.os = os
        self.parser = parser
        self.kb_controller = kb_controller
        self.mouse_controller = mouse_controller
        self.sleep_fn = sleep_fn

    @classmethod
    def from_none(cls) -> "SendCommandProcessor":
        """To be filled during init."""
        return SendCommandProcessor(None, None, None, None, None)  # type: ignore

    def send(
        self,
        command: str,
        interval: float | None = None,
        press_duration: float | None = None,
        speed: float = 1,
    ) -> None:
        """
        Entry point, processes the command and sends instructions.

        :param command: What to send.
        :param interval: Time before each key/button press.
        :param press_duration: Time between key press and release, only applies on click, not on up/down.
        :param speed: All sleep commands are divided by this number. Does not influence interval or press_duration.
        """
        config = config_thread_local_storage.action_config
        interval = interval if interval is not None else config.send_interval
        press_duration = (
            press_duration if press_duration is not None else config.send_press_duration
        )

        instructions: list[SendInstruction] = self.parser.parse(
            command, self.shift_down()
        )
        for instruction in instructions:
            if isinstance(instruction, KeyInstruction):
                if (
                    instruction.dir in [constants.KeyDir.DOWN, constants.KeyDir.CLICK]
                    and interval
                ):
                    self.sleep_fn(interval)
                self._send_key_instruction(instruction, press_duration)
            elif isinstance(instruction, WheelInstruction):
                self.mouse_controller.press(instruction.wheel_symbol)
            elif isinstance(instruction, CursorMoveInstruction):
                self.mouse_controller.move(*instruction.xy, instruction.relative)
            elif isinstance(instruction, SleepInstruction):
                self.sleep_fn(instruction.time / speed)
            else:
                raise SendError

    def shift_down(self) -> str | None:
        """Determines which shift is down, if any."""
        for shift in ["left_shift", "right_shift"]:
            if self.kb_controller.pressed(shift):
                return shift
        return None

    def _send_key_instruction(self, ki: KeyInstruction, press_duration: float) -> None:
        symbol = ki.symbol
        cmd: KeyboardController | MouseController
        if symbol in keyboard.get_keys(self.os):
            cmd = self.kb_controller
        elif symbol in mouse.get_keys():
            cmd = self.mouse_controller
        else:
            raise SendError

        if ki.dir == constants.KeyDir.DOWN:
            cmd.press(symbol)
        elif ki.dir == constants.KeyDir.UP:
            cmd.release(symbol)
        elif ki.dir == constants.KeyDir.CLICK:
            self._click(cmd, symbol, press_duration)
        elif ki.dir == constants.KeyDir.ON:
            if not cmd.toggled(symbol):
                self._click(cmd, symbol, press_duration)
        elif ki.dir == constants.KeyDir.OFF:
            if cmd.toggled(symbol):
                self._click(cmd, symbol, press_duration)
        else:
            raise SendError

    def _click(
        self,
        cmd: KeyboardController | MouseController,
        symbol: str,
        press_duration: float,
    ) -> None:
        cmd.press(symbol)
        if press_duration:
            self.sleep_fn(press_duration)
        cmd.release(symbol)
