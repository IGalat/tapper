import time
from dataclasses import dataclass
from typing import Any
from typing import Callable

import tapper
from tapper.controller.mouse import mouse_api
from tapper.helper.helper_model import RecordConfig
from tapper.model.constants import KeyDir
from tapper.model.constants import KeyDirBool
from tapper.model.send import CursorMoveInstruction
from tapper.model.send import KeyInstruction
from tapper.model.send import SendInstruction
from tapper.model.send import SleepInstruction
from tapper.model.send import WheelInstruction
from tapper.model.types_ import Signal
from tapper.util import event


@dataclass
class SignalRecord:
    signal: Signal
    time: float
    mouse_pos: tuple[int, int] | None


recording: list[SignalRecord] | None = None
rconfig: RecordConfig | None = None

record_signal = lambda signal: recording.append(  # type: ignore
    SignalRecord(signal, time.perf_counter(), tapper.mouse.get_pos())
)


def toggle_recording(callback: Callable[[str], Any], config: RecordConfig) -> None:
    global recording
    timeout = lambda time2: time.perf_counter() - time2 > config.max_recording_time

    if recording is None or (recording and timeout(recording[0].time)):
        start_recording()
    else:
        stop_recording(callback, config)


def start_recording() -> None:
    global recording
    recording = []

    time.sleep(0.001)  # or it sometimes records DOWN of trigger
    event.subscribe("keyboard", record_signal)
    event.subscribe("mouse", record_signal)


def stop_recording(callback: Callable[[str], Any], config: RecordConfig) -> None:
    global recording

    event.unsubscribe("keyboard", record_signal)
    event.unsubscribe("mouse", record_signal)

    if recording:
        rec = recording
        recording = None
        callback(transform_recording(rec, config))


def transform_recording(records: list[SignalRecord], config: RecordConfig) -> str:
    start_buttons_number = first_with_dir(records, KeyDirBool.DOWN)
    inverted_stop = first_with_dir(list(reversed(records)), KeyDirBool.UP)

    if start_buttons_number == -1 or inverted_stop == -1:
        raise ValueError("No start/stop buttons detected.")
    if len(records) < start_buttons_number + inverted_stop + 1:
        return ""

    reduce_time(records, config.non_compress_action_delay)
    records_cut = records[start_buttons_number:-inverted_stop]
    reduce_mouse_moves(records_cut, config.min_mouse_movement)
    instructions = to_instructions(records_cut)
    if config.down_up_as_click:
        compress_down_ups(instructions)
    strs = to_strings(instructions)
    result = "$(" + ";".join(strs) + ")"
    return result


def first_with_dir(records: list[SignalRecord], dir: KeyDirBool) -> int:
    """First record with dir. Or -1 if not found."""
    return next((i for i in range(len(records)) if records[i].signal[1] == dir), -1)


def reduce_time(records: list[SignalRecord], non_compress_action_delay: float) -> None:
    """Removes small delays, rounds large ones. Sets record.time to delay instead of absolute."""
    for i in reversed(range(len(records) - 1)):
        if (diff := records[i + 1].time - records[i].time) > non_compress_action_delay:
            records[i + 1].time = round(diff, 2)
        else:
            records[i + 1].time = 0


def reduce_mouse_moves(records: list[SignalRecord], min_movement: int) -> None:
    """Removes small movement, setting record.mouse_pos to None."""
    pos = records[0].mouse_pos
    for i in range(len(records) - 1):
        r = records[i + 1]
        if r.mouse_pos and mouse_api.is_near(
            r.mouse_pos[0], r.mouse_pos[1], pos[0], pos[1], min_movement  # type: ignore
        ):
            r.mouse_pos = None
        else:
            pos = r.mouse_pos


def to_instructions(records: list[SignalRecord]) -> list[SendInstruction]:
    result: list[SendInstruction] = []
    for r in records:
        if r.time:
            result.append(SleepInstruction(r.time))
        if r.mouse_pos:
            result.append(CursorMoveInstruction(r.mouse_pos))
        symbol = r.signal[0]
        instruction = tapper._send_processor.parser.symbols[symbol](symbol)  # type: ignore
        if isinstance(instruction, KeyInstruction):
            if r.signal[1] == KeyDirBool.DOWN:
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
            result.append(f"{ins.time}s")
        else:
            raise TypeError(type(ins))
    return result
