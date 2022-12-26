from functools import partial
from typing import Any
from typing import Callable
from typing import Optional

import pytest
from tapper.model.window import Window


@pytest.mark.skip(
    reason="tox does not recognise win32con, some bug in pywin32? only manual for now"
)
class TestWin32WindowController:
    test_window = Window("title", "exec", 123, 456)
    handles_commanded: list[Any] = []

    @pytest.fixture
    def command_fns(self) -> list[Callable[[Any], Any]]:
        self.handles_commanded.clear()

        def command(handle: Any) -> None:
            self.handles_commanded.append(handle)

        return [command]

    @pytest.fixture
    def win_command(self, command_fns: list[Callable[[Any], Any]]) -> Any:
        from tapper.controller.window.window_win32_impl import win_filter

        from tapper.controller.window.window_win32_impl import (
            Win32WindowTrackerCommander,
        )

        def get_open(
            exec_or_title: Optional[str] = None,
            title: Optional[str] = None,
            exec: Optional[str] = None,
            strict: bool = False,
            process_id: Optional[int] = None,
            handle: Any = None,
            limit: Optional[int] = None,
        ) -> list[Window]:
            filtered = win_filter(
                self.test_window, exec_or_title, title, exec, strict, process_id, handle
            )
            return [filtered] if filtered else []

        win_tc = Win32WindowTrackerCommander()
        win_tc.get_open = get_open
        return partial(win_tc.window_commands, command_fns)

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

    def test_win_cmd_handle(self, win_command: Any) -> None:
        assert win_command(handle=987)
        assert self.handles_commanded[0] == 987
        self.handles_commanded.clear()

        assert win_command(handle=456)
        assert self.handles_commanded[0] == self.test_window.handle

    def test_win_cmd_pid(self, win_command: Any) -> None:
        assert not win_command(process_id=987)
        assert not self.handles_commanded
        assert win_command(process_id=123)
        assert self.handles_commanded[0] == self.test_window.handle

    def test_win_cmd_win(self, win_command: Any) -> None:
        assert not win_command("some")
        assert not self.handles_commanded
        assert win_command(self.test_window)
        assert self.handles_commanded[0] == self.test_window.handle

    def test_win_cmd_exec_or_title(self, win_command: Any) -> None:
        assert not win_command("some")
        assert not self.handles_commanded
        assert not win_command("tle", strict=True)
        assert not self.handles_commanded
        assert win_command("tle")
        assert self.handles_commanded[0] == self.test_window.handle
        self.handles_commanded.clear()

        assert not win_command("xec", strict=True)
        assert not self.handles_commanded
        assert win_command("xec")
        assert self.handles_commanded[0] == self.test_window.handle

    def test_win_cmd_title(self, win_command: Any) -> None:
        assert not win_command(title="some")
        assert not self.handles_commanded
        assert not win_command(title="tle", strict=True)
        assert not self.handles_commanded
        assert win_command(title="tle")
        assert self.handles_commanded[0] == self.test_window.handle

    def test_win_cmd_exec(self, win_command: Any) -> None:
        assert not win_command(exec="some")
        assert not self.handles_commanded
        assert not win_command(exec="xec", strict=True)
        assert not self.handles_commanded
        assert win_command(exec="xec")
        assert self.handles_commanded[0] == self.test_window.handle
