import sys

from tapper import trigger_conditions
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.window.window_api import WindowController
from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.constants import ListenerResult
from tapper.model.types_ import KwTriggerConditions
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener
from tapper.signal.mouse.mouse_listener import MouseSignalListener
from tapper.util.datastructs import get_first_in

"""
------------------------------------
SECTION 1: Most likely to be tweaked.
------------------------------------
"""

default_send_interval = 0.01
"""
Interval between clicks for send command.
This is just a default value. You can use a different one in each send:
    send("Hellow", interval=1)
"""

default_trigger_suppression = ListenerResult.SUPPRESS
"""
Will the triggering signal be suppressed for other apps, when a Tap triggers?
This is just a default value. You can use a different one individually:
    Tap("a", "b", suppress_trigger=ListenerResult.PROPAGATE)
    Group(suppress_trigger=ListenerResult.PROPAGATE)
"""

only_visible_windows = True
"""Limit windows to visible - ones that are open on the taskbar.
Reduces WindowController lag, and junk windows caught into filters."""

"""
------------------------------------
SECTION 2: Advanced usage.
------------------------------------
"""

action_runner_executors_threads: list[int] = [1]
"""Number of action executors(length of the list), and threads for each.

Setting value to N will allow N actions to execute simultaneously for a given executor.
"""

os = sys.platform

"""
------------------------------------
SECTION 3: Extending the functionality.
------------------------------------
"""

keys_held_down = lambda os_: [*keyboard.get_key_list(os_), *mouse.regular_buttons]
"""Keys that can be held down."""

listeners = [
    KeyboardSignalListener,
    MouseSignalListener,
]

controllers = [
    KeyboardController(),
    MouseController(),
    WindowController(),
]

kw_trigger_conditions: KwTriggerConditions = {
    **trigger_conditions.generic(),
    **trigger_conditions.keyboard(get_first_in(KeyboardController, controllers)),
    **trigger_conditions.mouse(get_first_in(MouseController, controllers)),
    **trigger_conditions.window(get_first_in(WindowController, controllers)),
}
"""
Keyword trigger conditions that can be used as part of Tap or Group.

When keyword is used, the value is used in the corresponding function every
time signal is received and Tap or Group could trigger an action.
bool(result) determines if Tap or Group is active for this signal or not.

Example:
    Tap("a", "b", exec_open="paint")

    "exec_open" is the key and value is a function that evaluates whether there
    is an open window that has exec like "paint".

    When:
    - signal "a" is received
    - nothing is triggered before this Tap
    - parent Groups are active (not suspended or failed a check like this)
    - the value function is called with positional-1 arg "paint", and bool(result):
    Tap's action "b" will be executed!
"""
