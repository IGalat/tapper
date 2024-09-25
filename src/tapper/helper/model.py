from dataclasses import dataclass


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
