class NotSubstitutedError(UnboundLocalError):
    """The function should be substituted at init time but wasn't."""


class TriggerParseError(ValueError):
    """Incorrectly specified trigger text."""


class SendParseError(ValueError):
    """Incorrectly specified send command text."""


class SendError(ValueError):
    """A generic "send" command error."""
