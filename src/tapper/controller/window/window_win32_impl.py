import ctypes.wintypes
import os
import time
from typing import Any
from typing import Callable
from typing import Optional

import pywintypes
import win32api
import win32con
import win32gui
import win32process

from tapper.controller.window.window_api import WindowDriver
from tapper.feedback.logger import log
from tapper.model.window import Window

user32 = ctypes.windll.user32  # type: ignore  # only typed and imported on Windows
ole32 = ctypes.windll.ole32  # type: ignore  # only typed and imported on Windows
kernel32 = ctypes.windll.kernel32  # type: ignore  # only typed and imported on Windows

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


def str_match(filtered: str, iterated: str | None, strict: bool) -> bool:
    if not filtered or not iterated:
        return False
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
    if title and not str_match(title, win.title, strict):
        return None
    return win


OPEN_WINDOWS_TTL = 0.1
"""Enumerating windows with their exec names takes milliseconds, and `open_win`
conditions ask on every keystroke, so a recent enumeration is reused for this long."""


class Win32WindowDriver(WindowDriver):
    only_visible_windows: bool
    _open_windows: list[Window]
    _open_windows_at: float

    def __init__(self, only_visible_windows: bool = True) -> None:
        self.only_visible_windows = only_visible_windows
        self._open_windows = []
        self._open_windows_at = float("-inf")

    def _all_open(self) -> list[Window]:
        now = time.perf_counter()
        if now - self._open_windows_at > OPEN_WINDOWS_TTL:
            found: list[Optional[Window]] = []
            win32gui.EnumWindows(
                lambda hwnd, _: found.append(self.to_window(hwnd)), None
            )
            self._open_windows = [win for win in found if win]
            self._open_windows_at = now
        return self._open_windows

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
        for win in self._all_open():
            if win_filter(win, exec_or_title, title, exec, strict, process_id, handle):
                result.append(win)
                if limit and len(result) >= limit:
                    break
        return result

    def active(
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

    def to_active(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        try:
            result = self.window_commands(
                [win32gui.SetForegroundWindow],
                window_or_exec_or_title,
                title,
                exec,
                strict,
                process_id,
                handle,
            )
        except pywintypes.error as e:
            log.warning(e)
            result = self._win_explorer_to_active(handle)
        if result:
            win32gui.ShowWindow(handle, win32con.SW_RESTORE)  # un-minimize
            return True
        else:
            return False

    def _win_explorer_to_active(self, handle: Any) -> bool:
        try:
            fg = user32.GetForegroundWindow()
            cur_tid = win32api.GetCurrentThreadId()
            tgt_tid, _ = win32process.GetWindowThreadProcessId(handle)
            fg_tid, _ = win32process.GetWindowThreadProcessId(fg or 0)
            if tgt_tid and tgt_tid != cur_tid:
                user32.AttachThreadInput(cur_tid, tgt_tid, True)
            if fg_tid and fg_tid != cur_tid:
                user32.AttachThreadInput(cur_tid, fg_tid, True)

            user32.BringWindowToTop(handle)
            user32.SetActiveWindow(handle)
            user32.SetForegroundWindow(handle)
            return True
        except Exception as e:
            log.error(e)
            return False

    def to_next_of_same_group(self) -> bool:
        active = self.active()
        if not active or not active.handle:
            return False

        all_of_this_exec = self.get_open(exec=active.exec)
        if len(all_of_this_exec) < 2:
            return False
        if all_of_this_exec[0].exec != active.exec:
            return False

        return self.to_active(handle=all_of_this_exec[1].handle)

    def close(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
        force_after: Optional[float] = None,
    ) -> bool:
        if (
            window_or_exec_or_title is None
            and title is None
            and exec is None
            and process_id is None
            and handle is None
        ):
            win = self.get_open(handle=win32gui.GetForegroundWindow(), limit=1)
            window = win[0] if win else None
        elif window_or_exec_or_title is not None and isinstance(
            window_or_exec_or_title, Window
        ):
            window = window_or_exec_or_title
        else:
            win = self.get_open(
                window_or_exec_or_title, title, exec, strict, process_id, handle, 1
            )
            window = win[0] if win else None

        if not window:
            return False

        self.window_commands([destroy_command], handle=window.handle)

        if force_after is None:
            return True
        time.sleep(force_after)
        if self.get_open(handle=window.handle):
            os.system(f"taskkill /f /pid {window.process_id}")
        return True

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
        if (
            window_or_exec_or_title is None
            and title is None
            and exec is None
            and process_id is None
            and handle is None
        ):
            handle = win32gui.GetForegroundWindow()

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
        try:
            [cmd(open_win[0].handle) for cmd in commands_for_handle]
        except Exception as e:
            log.error(e)
            return False
        return True
