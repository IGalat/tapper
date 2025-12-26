import uuid
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable


@dataclass
class RecordConfig:
    """Config for record function. And properties of transformation to string."""

    max_recording_time: float = 15 * 60
    """Max time of recording, in seconds.
    If this is reached, toggle will switch to activating new recording."""

    max_compress_action_interval: float = 0.5
    """If time between signals is longer than this, it won't be compressed."""

    down_up_as_click: bool = True
    """Transform UP and DOWN key to CLICK key."""

    min_mouse_movement: int = 0
    """Mouse movements less than this will be disregarded."""

    shorten_to_aliases: bool = True
    """Will swap "left_mouse_button" with "lmb", "left_control" with "lctrl" etc."""

    cut_start_stop: bool = True
    """Will cut start and stop keys out of recording."""

    end_cut_time: float = 0.05
    """If cut_start_stop is on, this time before end of recording will be cut.
    Responsible for not recording hotkeys that stop recording."""


@dataclass
class Repeatable:
    """Repeatable action and properties."""

    condition: Callable[[], Any]
    """Will be checked every time, with bool(result) used for evaluating."""

    action: Callable[[], Any]
    """What to repeat."""

    uid: uuid.UUID = field(default_factory=uuid.uuid4)

    interval: float = 0.1
    """Time between repeats in seconds."""

    max_repeats: int | None = None
