import sys

from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.model import keyboard
from tapper.model import mouse
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener
from tapper.signal.mouse.mouse_listener import MouseSignalListener

"""
SECTION 1: Most likely to be tweaked.
"""


"""
SECTION 2: Advanced usage.
"""

action_runner_executors_threads: list[int] = [1]
"""Number of action executors(length of the list), and threads for each.

Setting value to N will allow N actions to execute simultaneously for a given executor.
"""

os = sys.platform


"""
SECTION 3: Extending the functionality.
"""

listeners = [
    KeyboardSignalListener,
    MouseSignalListener,
]

controllers = [
    KeyboardController(),
    MouseController(),
]

keys_held_down = lambda os_: [*keyboard.get_key_list(os_), *mouse.regular_buttons]
"""Keys that can be held down."""
