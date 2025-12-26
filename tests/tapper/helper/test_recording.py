from typing import Generator
from unittest.mock import patch

import pytest
from tapper.helper import recording
from tapper.helper._util import record_util
from tapper.helper._util.record_util import SignalRecord
from tapper.helper.model import RecordConfig
from tapper.model.constants import KeyDirBool
from tapper.model.types_ import Signal
from tapper.util import event
from testutil_model import FakeClock


def wrap_in_start_stop(records: list[SignalRecord]) -> list[SignalRecord]:
    return [
        SignalRecord(("a", KeyDirBool.UP), 0, None),
        *records,
        SignalRecord(("b", KeyDirBool.DOWN), 100, (700, 700)),
    ]


class TestRecorderTransform:
    def test_simplest(self) -> None:
        result = record_util.transform_recording([], RecordConfig(cut_start_stop=False))
        assert result == ""

    def test_cut_simplest(self, fake_perf_counter) -> None:
        result = record_util.transform_recording(wrap_in_start_stop([]), RecordConfig())
        fake_perf_counter.set(100)
        assert result == ""

    def test_cut_with_content(self, fake_perf_counter) -> None:
        record = wrap_in_start_stop(
            [
                SignalRecord(("q", KeyDirBool.DOWN), 0, None),
                SignalRecord(("q", KeyDirBool.UP), 0, None),
                SignalRecord(("w", KeyDirBool.DOWN), 0, None),
                SignalRecord(("w", KeyDirBool.UP), 0, None),
                SignalRecord(("e", KeyDirBool.DOWN), 0, None),
                SignalRecord(("e", KeyDirBool.UP), 0, None),
            ]
        )
        fake_perf_counter.set(100)
        result = record_util.transform_recording(
            record, RecordConfig(down_up_as_click=True)
        )
        assert result == "$(q;w;e)"

    def test_cut_combo_start_wrap(self, fake_perf_counter) -> None:
        record = [
            SignalRecord(("control", KeyDirBool.UP), 0, None),
            SignalRecord(("8", KeyDirBool.UP), 0, None),
            SignalRecord(("q", KeyDirBool.DOWN), 0, None),
            SignalRecord(("q", KeyDirBool.UP), 0, None),
            SignalRecord(("w", KeyDirBool.DOWN), 0, None),
            SignalRecord(("w", KeyDirBool.UP), 0, None),
            SignalRecord(("e", KeyDirBool.DOWN), 0, None),
            SignalRecord(("e", KeyDirBool.UP), 0, None),
            SignalRecord(("control", KeyDirBool.DOWN), 100, None),
            SignalRecord(("9", KeyDirBool.DOWN), 100, None),
        ]
        fake_perf_counter.set(100)
        result = record_util.transform_recording(
            record, RecordConfig(down_up_as_click=True)
        )
        assert result == "$(q;w;e)"

    def test_max_compress_action_interval(self, fake_perf_counter) -> None:
        record = wrap_in_start_stop(
            [
                SignalRecord(("q", KeyDirBool.DOWN), 0, None),
                SignalRecord(("q", KeyDirBool.UP), 0.2, None),
                SignalRecord(("w", KeyDirBool.DOWN), 1.1, None),
                SignalRecord(("w", KeyDirBool.UP), 4.1, None),
                SignalRecord(("e", KeyDirBool.DOWN), 4.5, None),
                SignalRecord(("e", KeyDirBool.UP), 6.001, None),  # should be rounded
            ]
        )
        fake_perf_counter.set(100)
        result = record_util.transform_recording(
            record, RecordConfig(down_up_as_click=False, max_compress_action_interval=1)
        )
        assert result == "$(q down;q up;w down;3s;w up;e down;1.5s;e up)"

    def test_down_up_as_click(self, fake_perf_counter) -> None:
        record = wrap_in_start_stop(
            [
                SignalRecord(("q", KeyDirBool.DOWN), 0, None),
                SignalRecord(("q", KeyDirBool.UP), 0.2, None),
                SignalRecord(("w", KeyDirBool.DOWN), 1.1, None),
                SignalRecord(("w", KeyDirBool.UP), 4.1, None),
                SignalRecord(("e", KeyDirBool.DOWN), 4.5, None),
                SignalRecord(("e", KeyDirBool.UP), 5.001, None),
            ]
        )
        fake_perf_counter.set(100)
        result = record_util.transform_recording(
            record, RecordConfig(down_up_as_click=True, max_compress_action_interval=1)
        )
        assert result == "$(q;w down;3s;w up;e)"

    def test_min_mouse_movement(self, fake_perf_counter) -> None:
        record = wrap_in_start_stop(
            [
                SignalRecord(("q", KeyDirBool.DOWN), 0, (0, 0)),
                SignalRecord(("q", KeyDirBool.UP), 0, (0, 0)),
                SignalRecord(("w", KeyDirBool.DOWN), 0, (100, 100)),
                SignalRecord(("w", KeyDirBool.UP), 0, (200, 200)),
                SignalRecord(("e", KeyDirBool.DOWN), 0, (200, 208)),
                SignalRecord(("e", KeyDirBool.UP), 0, (200, 208)),
                # should be detected since total movement is more
                SignalRecord(("r", KeyDirBool.DOWN), 0, (200, 216)),
                SignalRecord(("r", KeyDirBool.UP), 0, (200, 216)),
            ]
        )
        fake_perf_counter.set(100)
        result = record_util.transform_recording(
            record, RecordConfig(down_up_as_click=True, min_mouse_movement=10)
        )
        assert result == "$(x0y0;q;x100y100;w down;x200y200;w up;e;x200y216;r)"

    def test_shorten_to_aliases(self, fake_perf_counter) -> None:
        record = wrap_in_start_stop(
            [
                SignalRecord(("escape", KeyDirBool.DOWN), 0, None),
                SignalRecord(("escape", KeyDirBool.UP), 0, None),
                SignalRecord(("left_control", KeyDirBool.DOWN), 0, None),
                SignalRecord(("left_control", KeyDirBool.UP), 0, None),
                SignalRecord(("right_mouse_button", KeyDirBool.DOWN), 0, None),
                SignalRecord(("right_mouse_button", KeyDirBool.UP), 0, None),
            ]
        )
        fake_perf_counter.set(100)
        result = record_util.transform_recording(
            record, RecordConfig(down_up_as_click=True, shorten_to_aliases=True)
        )
        assert result == "$(esc;lctrl;rmb)"


def push_key(signal: Signal, fake_clock: FakeClock) -> None:
    event.publish("keyboard", signal)
    fake_clock.advance(1)


class TestRecording:
    config = RecordConfig(max_compress_action_interval=1.5, end_cut_time=1.5)

    @pytest.fixture(autouse=True)
    def mock_mouse_pos(self) -> Generator:
        with patch("tapper.mouse.get_pos") as mock_pos:
            mock_pos.return_value = (0, 0)
            yield

    @pytest.fixture
    def mock_send(self) -> Generator:
        with patch("tapper.helper.recording.send") as mock_send:
            yield mock_send

    def test_simplest(self, mock_sleep, fake_perf_counter) -> None:
        recording.start()()

        push_key(("8", KeyDirBool.UP), fake_perf_counter)

        push_key(("q", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("q", KeyDirBool.UP), fake_perf_counter)
        push_key(("w", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("w", KeyDirBool.UP), fake_perf_counter)
        push_key(("e", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("e", KeyDirBool.UP), fake_perf_counter)

        push_key(("8", KeyDirBool.DOWN), fake_perf_counter)

        recording.stop(config=self.config)()
        assert recording.last_recorded == "$(x0y0;q;w;e)"

    def test_toggle(self, mock_sleep, fake_perf_counter) -> None:
        toggle = recording.toggle(config=self.config)
        toggle()

        push_key(("8", KeyDirBool.UP), fake_perf_counter)

        push_key(("q", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("q", KeyDirBool.UP), fake_perf_counter)
        push_key(("w", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("w", KeyDirBool.UP), fake_perf_counter)
        push_key(("e", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("e", KeyDirBool.UP), fake_perf_counter)

        push_key(("8", KeyDirBool.DOWN), fake_perf_counter)

        toggle()
        assert recording.last_recorded == "$(x0y0;q;w;e)"

    def test_start_toggle(self, mock_sleep, fake_perf_counter) -> None:
        toggle = recording.toggle(config=self.config)
        recording.start()()

        push_key(("8", KeyDirBool.UP), fake_perf_counter)

        push_key(("q", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("q", KeyDirBool.UP), fake_perf_counter)
        push_key(("w", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("w", KeyDirBool.UP), fake_perf_counter)
        push_key(("e", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("e", KeyDirBool.UP), fake_perf_counter)

        push_key(("8", KeyDirBool.DOWN), fake_perf_counter)

        toggle()
        assert recording.last_recorded == "$(x0y0;q;w;e)"

    def test_playback_action(self, mock_sleep, fake_perf_counter) -> None:
        recording.start()()

        push_key(("8", KeyDirBool.UP), fake_perf_counter)

        push_key(("q", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("q", KeyDirBool.UP), fake_perf_counter)
        push_key(("w", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("w", KeyDirBool.UP), fake_perf_counter)
        push_key(("e", KeyDirBool.DOWN), fake_perf_counter)
        push_key(("e", KeyDirBool.UP), fake_perf_counter)

        push_key(("8", KeyDirBool.DOWN), fake_perf_counter)

        recording.stop(config=self.config)()

        with patch("tapper.helper.recording.send") as mock_send:
            recording.action_playback_last(speed=2)()

            assert mock_send.called
            args, kwargs = mock_send.call_args
            assert args == ("$(x0y0;q;w;e)",)
            assert kwargs["speed"] == 2
