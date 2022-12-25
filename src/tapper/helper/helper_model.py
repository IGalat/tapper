from dataclasses import dataclass


@dataclass
class RecordConfig:
    """Config for record function. And properties of transformation to string."""

    max_recording_time: float = 15 * 60
    """Max time of recording. If this is reached, toggle will switch to activating new recording."""

    non_compress_action_delay: float = 0.5
    """If time between signals is longer than this, it won't be compressed."""

    down_up_as_click: bool = True
    """Transform UP and DOWN key to CLICK key."""

    min_mouse_movement: int = 50
    """Mouse movements less than this will be disregarded."""
