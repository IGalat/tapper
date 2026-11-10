# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper"]
# ///
# Windows only: the same key does different things depending on the active app.
from tapper import Group
from tapper import start

start(
    Group(win_exec="chrome.exe").add(
        {
            "f1": "$(ctrl+t)",  # new tab
            "f2": "$(ctrl+shift+t)",  # reopen closed tab
        }
    ),
    Group(win="notepad").add({"f1": "$(ctrl+s)"}),  # save instead of opening help
)
