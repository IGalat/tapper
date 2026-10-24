import sys
from collections.abc import Callable
from functools import partial
from typing import Any

import pytest

from tapper.model.window import Window
from testutil_model import FakeClock


@pytest.mark.skipif(sys.platform != "win32", reason="imports pywin32")
def test_get_open_reuses_enumeration_within_ttl(
    monkeypatch: pytest.MonkeyPatch, fake_perf_counter: FakeClock
) -> None:
    from tapper.controller.window import window_win32_impl as impl

    windows = [
        Window("Notepad", "notepad.exe", 1, 10),
        Window("Chrome", "chrome.exe", 2, 20),
    ]
    enumerations = 0

    def enum_windows(callback: Callable[[Any, Any], Any], _: Any) -> None:
        nonlocal enumerations
        enumerations += 1
        for win in windows:
            callback(win.handle, None)

    monkeypatch.setattr(impl.win32gui, "EnumWindows", enum_windows)
    tracker = impl.Win32WindowDriver()
    monkeypatch.setattr(
        tracker, "to_window", lambda hwnd: next(w for w in windows if w.handle == hwnd)
    )

    fake_perf_counter.set(10)
    assert tracker.get_open("notepad") == [windows[0]]
    assert tracker.get_open(exec="chrome.exe", strict=True) == [windows[1]]
    assert tracker.get_open(limit=1) == [windows[0]]
    assert enumerations == 1

    fake_perf_counter.advance(impl.OPEN_WINDOWS_TTL + 0.001)
    assert tracker.get_open() == windows
    assert enumerations == 2


@pytest.mark.skipif(sys.platform != "win32", reason="imports pywin32")
class TestWin32WindowController:
    test_window = Window("title", "exec", 123, 456)

    @pytest.fixture
    def commanded(self) -> list[Any]:
        return []

    @pytest.fixture
    def win_command(self, commanded: list[Any], monkeypatch: pytest.MonkeyPatch) -> Any:
        from tapper.controller.window.window_win32_impl import Win32WindowDriver
        from tapper.controller.window.window_win32_impl import win_filter

        def get_open(
            exec_or_title: str | None = None,
            title: str | None = None,
            exec: str | None = None,
            strict: bool = False,
            process_id: int | None = None,
            handle: Any = None,
            limit: int | None = None,
        ) -> list[Window]:
            filtered = win_filter(
                self.test_window, exec_or_title, title, exec, strict, process_id, handle
            )
            return [filtered] if filtered else []

        driver = Win32WindowDriver()
        monkeypatch.setattr(driver, "get_open", get_open)
        return partial(driver.window_commands, [commanded.append])

    def test_win_filter_none(self) -> None:
        from tapper.controller.window.window_win32_impl import win_filter

        assert win_filter(None) is None

    def test_win_filter_no_conditions(self) -> None:
        from tapper.controller.window.window_win32_impl import win_filter

        win = Window(title="s", exec="r")
        assert win_filter(win) == win

    def test_win_filter_exec_or_title(self) -> None:
        from tapper.controller.window.window_win32_impl import win_filter

        win = Window(title="NOTepad")
        assert win_filter(win, "otep") == win

        win.title = None
        win.exec = "NOTePad"
        assert win_filter(win, "otep") == win

    def test_win_filter_exec_or_title_strict(self) -> None:
        from tapper.controller.window.window_win32_impl import win_filter

        win = Window(title="NOTepad")
        assert win_filter(win, "otep", strict=True) is None
        assert win_filter(win, "NOTepad", strict=True) == win

        win.title = None
        win.exec = "NOTePad"
        assert win_filter(win, "otep", strict=True) is None
        assert win_filter(win, "NOTePad", strict=True) == win

    def test_win_filter_title(self) -> None:
        from tapper.controller.window.window_win32_impl import win_filter

        win = Window(title="idea")
        assert win_filter(win, title="ide") == win
        assert win_filter(win, exec="ide") is None

    def test_win_filter_exec(self) -> None:
        from tapper.controller.window.window_win32_impl import win_filter

        win = Window(exec="idea")
        assert win_filter(win, exec="dea") == win
        assert win_filter(win, title="dea") is None

    def test_win_filter_handle(self) -> None:
        from tapper.controller.window.window_win32_impl import win_filter

        win = Window(handle=123)
        assert win_filter(win, handle=123) == win
        assert win_filter(win, handle=12) is None

    def test_win_filter_pid(self) -> None:
        from tapper.controller.window.window_win32_impl import win_filter

        win = Window(process_id=123)
        assert win_filter(win, process_id=123) == win
        assert win_filter(win, process_id=12) is None

    def test_win_cmd_handle(self, win_command: Any, commanded: list[Any]) -> None:
        assert win_command(handle=987)
        assert commanded == [987]

        commanded.clear()
        assert win_command(handle=456)
        assert commanded == [self.test_window.handle]

    def test_win_cmd_pid(self, win_command: Any, commanded: list[Any]) -> None:
        assert not win_command(process_id=987)
        assert not commanded
        assert win_command(process_id=123)
        assert commanded == [self.test_window.handle]

    def test_win_cmd_win(self, win_command: Any, commanded: list[Any]) -> None:
        assert not win_command("some")
        assert not commanded
        assert win_command(self.test_window)
        assert commanded == [self.test_window.handle]

    def test_win_cmd_exec_or_title(
        self, win_command: Any, commanded: list[Any]
    ) -> None:
        assert not win_command("some")
        assert not win_command("tle", strict=True)
        assert not commanded
        assert win_command("tle")
        assert commanded == [self.test_window.handle]

        commanded.clear()
        assert not win_command("xec", strict=True)
        assert not commanded
        assert win_command("xec")
        assert commanded == [self.test_window.handle]

    def test_win_cmd_title(self, win_command: Any, commanded: list[Any]) -> None:
        assert not win_command(title="some")
        assert not win_command(title="tle", strict=True)
        assert not commanded
        assert win_command(title="tle")
        assert commanded == [self.test_window.handle]

    def test_win_cmd_exec(self, win_command: Any, commanded: list[Any]) -> None:
        assert not win_command(exec="some")
        assert not win_command(exec="xec", strict=True)
        assert not commanded
        assert win_command(exec="xec")
        assert commanded == [self.test_window.handle]
