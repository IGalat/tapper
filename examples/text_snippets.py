# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper"]
# ///
# tapper has no hotstrings (::btw::); bind snippets to keys instead.
# Shift is fine as a modifier: send works around a held shift, but not a held ctrl or alt.
import time

from tapper import send
from tapper import start

print("""Text snippets. Go to any text field, then:

    shift+F9    Types an email.
    shift+F10   Types a signature.
    shift+F11   Types today's date.

    F3          Restarts.
    alt+F3      Quits.""")
start(
    {
        "shift+f9": "me@example.com",
        "shift+f10": "Best regards,\nYour Name",
        "shift+f11": lambda: send(time.strftime("%Y-%m-%d")),
    }
)
