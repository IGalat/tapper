import time
from dataclasses import dataclass
from typing import Any
from typing import Callable

from tapper import config as tapper_config
from tapper import controller
from tapper import model
from tapper import mouse
from tapper.boot import initializer
from tapper.helper.model import RecordConfig
from tapper.model import keyboard
from tapper.model.constants import KeyDir
from tapper.model.constants import KeyDirBool
from tapper.model.send import CursorMoveInstruction
from tapper.model.send import KeyInstruction
from tapper.model.send import SendInstruction
from tapper.model.send import SleepInstruction
from tapper.model.send import WheelInstruction
from tapper.model.types_ import Signal
from tapper.model.types_ import SymbolsWithAliases
from tapper.util import event


def calc_short_aliases(aliases: SymbolsWithAliases) -> dict[str, str]:
    result: dict[str, str] = {}
    for alias, refs in aliases.items():
        ref = refs[0]
        if len(refs) > 1 or len(alias) >= len(ref):
            continue
        if ref not in result or len(result[ref]) > len(alias):
            result[ref] = alias
    return result


preferred_aliases: dict[str, str] = calc_short_aliases(
    {**keyboard.aliases, **model.mouse.button_aliases, **model.mouse.wheel_aliases}
)


@dataclass
class SignalRecord:
    signal: Signal
    time: float
    """Actual time of signal"""
    mouse_pos: tuple[int, int] | None
    """At time signal is recorded. Mouse movements are not recorded."""


recording_: list[SignalRecord] | None = None

record_signal = lambda signal: recording_.append(  # type: ignore
    SignalRecord(signal, time.time(), mouse.get_pos())
)


def toggle_recording(
    callbacks: list[Callable[[str], Any]], config: RecordConfig
) -> None:
    global recording_
    timeout = lambda time2: time.perf_counter() - time2 > config.max_recording_time

    if recording_ is None or (recording_ and timeout(recording_[0].time)):
        start_recording()
    else:
        stop_recording(callbacks, config)


def start_recording() -> None:
    global recording_
    recording_ = []

    time.sleep(0)  # or it sometimes records DOWN of trigger
    event.subscribe("keyboard", record_signal)
    event.subscribe("mouse", record_signal)


def stop_recording(callbacks: list[Callable[[str], Any]], config: RecordConfig) -> None:
    global recording_

    event.unsubscribe("keyboard", record_signal)
    event.unsubscribe("mouse", record_signal)

    if recording_:
        rec = recording_
        recording_ = None
        transformed = transform_recording(rec, config)
        [callback(transformed) for callback in callbacks]


def transform_recording(records: list[SignalRecord], config: RecordConfig) -> str:
    if config.cut_start_stop:
        records = cut_start_stop(records)
    if records:
        reduce_time(records, config.max_compress_action_interval)
        reduce_mouse_moves(records, config.min_mouse_movement)
    instructions = to_instructions(records)
    if config.down_up_as_click:
        compress_down_ups(instructions)
    strs = to_strings(instructions)
    result = join_parsed_instructions(strs)
    return result


def cut_start_stop(records: list[SignalRecord]) -> list[SignalRecord]:
    start_buttons_number = first_with_dir(records, KeyDirBool.DOWN)
    inverted_stop = first_with_dir(list(reversed(records)), KeyDirBool.UP)

    if start_buttons_number == -1 or inverted_stop == -1:
        raise ValueError("No start/stop buttons detected.")
    if len(records) < start_buttons_number + inverted_stop + 1:
        return []

    return records[start_buttons_number:-inverted_stop]


def first_with_dir(records: list[SignalRecord], dir: KeyDirBool) -> int:
    """First record with dir. Or -1 if not found."""
    return next((i for i in range(len(records)) if records[i].signal[1] == dir), -1)


def reduce_time(records: list[SignalRecord], non_compress_action_delay: float) -> None:
    """Removes small delays. Sets record.time to delay instead of absolute."""
    for i in reversed(range(len(records) - 1)):
        if (diff := records[i + 1].time - records[i].time) > non_compress_action_delay:
            records[i + 1].time = diff
        else:
            records[i + 1].time = 0
    records[0].time = 0


def reduce_mouse_moves(records: list[SignalRecord], min_movement: int) -> None:
    """Removes small movement, setting record.mouse_pos to None."""
    if not records:
        return
    pos = records[0].mouse_pos
    for i in range(len(records) - 1):
        r = records[i + 1]
        if r.mouse_pos and controller.mouse.mouse_api.is_near(
            r.mouse_pos[0], r.mouse_pos[1], pos[0], pos[1], min_movement  # type: ignore
        ):
            r.mouse_pos = None
        else:
            pos = r.mouse_pos


def to_instructions(records: list[SignalRecord]) -> list[SendInstruction]:
    result: list[SendInstruction] = []
    for record in records:
        if record.time:
            result.append(SleepInstruction(record.time))
        if record.mouse_pos:
            result.append(CursorMoveInstruction(record.mouse_pos))
        symbol = record.signal[0]
        if symbol in preferred_aliases:
            symbol = preferred_aliases[symbol]
        meta_instruction = initializer.get_symbols(tapper_config.os)[symbol]
        instruction = meta_instruction(symbol)  # type: ignore
        if isinstance(instruction, KeyInstruction):
            if record.signal[1] == KeyDirBool.DOWN:
                instruction.dir = KeyDir.DOWN
            else:
                instruction.dir = KeyDir.UP
        elif not isinstance(instruction, WheelInstruction):
            raise TypeError(f"Got instruction type {type(instruction)}")
        result.append(instruction)
    return result


def compress_down_ups(instructions: list[SendInstruction]) -> None:
    """Swaps a(UP), a(DOWN) for a(CLICK)."""
    for i in reversed(range(len(instructions))):
        if i >= len(instructions) - 1:
            continue
        in0 = instructions[i]
        in1 = instructions[i + 1]
        if isinstance(in0, KeyInstruction) and isinstance(in1, KeyInstruction):
            if (
                in0.dir == KeyDir.DOWN
                and in1.dir == KeyDir.UP
                and in0.symbol == in1.symbol
            ):
                instructions.pop(i)
                instructions.pop(i)
                instructions.insert(i, KeyInstruction(in0.symbol, KeyDir.CLICK))


def to_strings(instructions: list[SendInstruction]) -> list[str]:
    result = []
    for ins in instructions:
        if isinstance(ins, KeyInstruction):
            dir = ""
            if ins.dir == KeyDir.DOWN:
                dir = " down"
            elif ins.dir == KeyDir.UP:
                dir = " up"
            result.append(ins.symbol + dir)
        elif isinstance(ins, WheelInstruction):
            result.append(ins.wheel_symbol)
        elif isinstance(ins, CursorMoveInstruction):
            x, y = ins.xy
            result.append(f"x{x}y{y}")
        elif isinstance(ins, SleepInstruction):
            result.append(f"{ins.time:.3g}s")
        else:
            raise TypeError(type(ins))
    return result


def join_parsed_instructions(instructions: list[str]) -> str:
    prefix, suffix = tapper_config.send_combo_wrap.split("_")
    return "$(" + ";".join(instructions) + ")"
