from dataclasses import dataclass


@dataclass
class RecordConfig:
    """Config for record function. And properties of transformation to string."""

    hotkey_buttons: int = 1
    """
    Number of buttons in hotkey that toggles recording.
    This number of actions will be cut from start and end of recording,
    as these are just for recording to start/stop.
    """
    max_recording_time: float = 15 * 60
    """Max time of recording. If this is reached, toggle will switch to activating new recording."""

    non_compress_action_delay: float = 0.5
    """If time between signals is longer than this, it won't be compressed."""
    compress_multi_action: bool = True
    """This will compress 'a;a' into 'a 2x'."""

    down_up_as_click: bool = True
    """Transform UP and DOWN key to CLICK key."""

    min_mouse_movement: int = 50
    """Mouse movements less than this will be disregarded."""
