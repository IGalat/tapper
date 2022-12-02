import sys

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

os: sys.platform


"""
SECTION 3: Extending the functionality.
"""

listeners = [
    KeyboardSignalListener,
    MouseSignalListener,
]
