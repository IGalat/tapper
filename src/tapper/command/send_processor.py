import time
from typing import Callable

from tapper.command.keyboard.keyboard_commander import KeyboardCommander
from tapper.command.mouse.mouse_commander import MouseCommander
from tapper.model import constants
from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.errors import SendError
from tapper.model.send import KeyInstruction
from tapper.model.send import SendInstruction
from tapper.model.send import SleepInstruction
from tapper.model.send import WheelInstruction
from tapper.parser.send_parser import SendParser


class SendCommandProcessor:
    """Highest-level component for "send" command."""

    os: str
    parser: SendParser
    kb_commander: KeyboardCommander
    mouse_commander: MouseCommander
    sleep_fn: Callable[[float], None] = time.sleep

    def __init__(
        self,
        os: str,
        parser: SendParser,
        kb_commander: KeyboardCommander,
        mouse_commander: MouseCommander,
    ) -> None:
        self.os = os
        self.parser = parser
        self.kb_commander = kb_commander
        self.mouse_commander = mouse_commander

    def send(self, command: str) -> None:
        """Entry point, processes the command and sends instructions."""
        instructions: list[SendInstruction] = self.parser.parse(command)
        for instruction in instructions:
            if isinstance(instruction, KeyInstruction):
                self._send_key_instruction(instruction)
            elif isinstance(instruction, WheelInstruction):
                self.mouse_commander.press(instruction.wheel_symbol)
            elif isinstance(instruction, SleepInstruction):
                self.sleep_fn(instruction.time)  # type: ignore  # https://github.com/python/mypy/issues/5485
            else:
                raise SendError

    def _send_key_instruction(self, ki: KeyInstruction) -> None:
        symbol = ki.symbol
        cmd: KeyboardCommander | MouseCommander
        if symbol in keyboard.get_keys(self.os):
            cmd = self.kb_commander
        elif symbol in mouse.get_keys():
            cmd = self.mouse_commander
        else:
            raise SendError

        if ki.dir == constants.KeyDir.DOWN:
            cmd.press(symbol)
        elif ki.dir == constants.KeyDir.UP:
            cmd.release(symbol)
        elif ki.dir == constants.KeyDir.CLICK:
            cmd.press(symbol)
            cmd.release(symbol)
        elif ki.dir == constants.KeyDir.ON:
            if not cmd.toggled(symbol):
                cmd.press(symbol)
                cmd.release(symbol)
        elif ki.dir == constants.KeyDir.OFF:
            if cmd.toggled(symbol):
                cmd.press(symbol)
                cmd.release(symbol)
        else:
            raise SendError
