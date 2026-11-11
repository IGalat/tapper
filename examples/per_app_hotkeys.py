# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper==2026.11.1"]
# ///
from tapper import Group
from tapper import start

print("""Per-app hotkeys (Windows only). The same key does different things in each app:

    F1      In Chrome: opens a new tab. In Notepad: saves.
    F2      In Chrome: reopens the last closed tab.

    F3      Restarts.
    alt+F3  Quits.""")
start(
    Group(win_exec="chrome.exe").add(
        {
            "f1": "$(ctrl+t)",
            "f2": "$(ctrl+shift+t)",
        }
    ),
    Group(win="notepad").add({"f1": "$(ctrl+s)"}),
)
