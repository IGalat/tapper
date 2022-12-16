import ctypes.wintypes
from typing import Any
from typing import Callable
from typing import Optional

import win32con
import win32gui
from tapper.controller.window.window_api import WindowCommander
from tapper.controller.window.window_api import WindowTracker
from tapper.model.window import Window

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32

# https://learn.microsoft.com/en-us/windows/win32/menurc/wm-syscommand

processFlag = getattr(
    win32con,
    "PROCESS_QUERY_LIMITED_INFORMATION",
    win32con.WM_SYSCOMMAND,
)

minimize_command = lambda hwnd: win32gui.PostMessage(
    hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0
)

restore_command = lambda hwnd: win32gui.PostMessage(
    hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0
)

maximize_command = lambda hwnd: win32gui.PostMessage(
    hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MAXIMIZE, 0
)

destroy_command = lambda hwnd: win32gui.PostMessage(
    hwnd, win32con.WM_SYSCOMMAND, win32con.SC_CLOSE, 0
)


def get_pid(hwnd: Any) -> Optional[int]:
    process_id = None
    if hwnd:
        ulong = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(ulong))
        if ulong:
            process_id = int(ulong.value)
    return process_id


def get_process_exec(pid: Optional[int]) -> Optional[str]:
    h_process = kernel32.OpenProcess(processFlag, 0, pid)
    if not h_process:
        return None
    try:
        filename_buffer_size = ctypes.wintypes.DWORD(4096)
        filename = ctypes.create_unicode_buffer(filename_buffer_size.value)
        kernel32.QueryFullProcessImageNameW(
            h_process, 0, ctypes.byref(filename), ctypes.byref(filename_buffer_size)
        )
        return filename.value
    finally:
        kernel32.CloseHandle(h_process)


def str_match(filtered: str, iterated: str, strict: bool) -> bool:
    if strict:
        return filtered == iterated
    else:
        return filtered.casefold() in iterated.casefold()


def win_filter(
    win: Optional[Window],
    exec_or_title: Optional[str] = None,
    title: Optional[str] = None,
    exec: Optional[str] = None,
    strict: bool = False,
    process_id: Optional[int] = None,
    handle: Any = None,
) -> Optional[Window]:
    if not win:
        return None
    if handle and win.handle != handle:
        return None
    if process_id and win.process_id != process_id:
        return None
    if (
        exec_or_title
        and not str_match(exec_or_title, win.exec, strict)
        and not str_match(exec_or_title, win.title, strict)
    ):
        return None
    if exec and not str_match(exec, win.exec, strict):
        return None
    if title and not str_match(title, win.exec, strict):
        return None
    return win


def add_win_if_required(
    result: list[Window],
    exec_or_title: Optional[str] = None,
    title: Optional[str] = None,
    exec: Optional[str] = None,
    strict: bool = False,
    process_id: Optional[int] = None,
    handle: Any = None,
    limit: Optional[int] = None,
    win_to_add: Window = None,  # type: ignore
) -> None:
    if limit and len(result) >= limit:
        return
    if not hasattr(win_to_add, "exec") and not hasattr(win_to_add, "title"):
        return
    if win_filter(win_to_add, exec_or_title, title, exec, strict, process_id, handle):
        result.append(win_to_add)


class Win32WindowTrackerCommander(WindowTracker, WindowCommander):
    only_visible_windows: bool

    def __init__(self, only_visible_windows: bool = True) -> None:
        self.only_visible_windows = only_visible_windows

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_open(
        self,
        exec_or_title: Optional[str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
        limit: Optional[int] = None,
    ) -> list[Window]:
        result: list[Window] = []
        win32gui.EnumWindows(
            lambda hwnd, _: add_win_if_required(
                result,
                exec_or_title,
                title,
                exec,
                strict,
                process_id,
                handle,
                limit,
                self.to_window(hwnd),
            ),
            None,
        )
        return result

    def is_fore(
        self,
        exec_or_title: Optional[str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> Optional[Window]:
        fore = self.to_window(win32gui.GetForegroundWindow())
        return win_filter(fore, exec_or_title, title, exec, strict, process_id, handle)

    def to_fore(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        return self.window_commands(
            [win32gui.SetForegroundWindow],
            window_or_exec_or_title,
            title,
            exec,
            strict,
            process_id,
            handle,
        )

    def close(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        return self.window_commands(
            [destroy_command],
            window_or_exec_or_title,
            title,
            exec,
            strict,
            process_id,
            handle,
        )

    def minimize(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        return self.window_commands(
            [minimize_command],
            window_or_exec_or_title,
            title,
            exec,
            strict,
            process_id,
            handle,
        )

    def maximize(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        return self.window_commands(
            [maximize_command],
            window_or_exec_or_title,
            title,
            exec,
            strict,
            process_id,
            handle,
        )

    def restore(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        return self.window_commands(
            [restore_command],
            window_or_exec_or_title,
            title,
            exec,
            strict,
            process_id,
            handle,
        )

    def to_window(self, hwnd: Any) -> Optional[Window]:
        if self.only_visible_windows and not win32gui.IsWindowVisible(hwnd):
            return None
        text = win32gui.GetWindowText(hwnd)
        if text:
            pid = get_pid(hwnd)
            filename = get_process_exec(pid)
            if not filename:
                return None
            exec = "\\".join(filename.rsplit("\\", 2)[-1:])
            return Window(text, exec, pid, hwnd)
        return None

    def window_commands(
        self,
        commands_for_handle: list[Callable[[Any], Any]],
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        """Looks up the window handle and applies commands to it."""
        exec_or_title = None
        if isinstance(window_or_exec_or_title, Window):
            handle = window_or_exec_or_title.handle
        elif isinstance(window_or_exec_or_title, str):
            exec_or_title = window_or_exec_or_title

        if handle:
            [cmd(handle) for cmd in commands_for_handle]
            return True
        open_win = self.get_open(
            exec_or_title, title, exec, strict, process_id, handle, 1
        )
        if not open_win:
            return False
        [cmd(open_win[0].handle) for cmd in commands_for_handle]
        return True
