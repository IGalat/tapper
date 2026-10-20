"""Publisher-subscriber implementation.

Typical usage example:

To subscribe:
    event.subscribe(PREDEFINED_TOPIC_NAME, function_that_will_receive_messages)
(can be done in a different place than the subscriber)

In publisher:
    event.publish(PREDEFINED_TOPIC_NAME, message_of_any_type)

Subscribers are called on one worker thread, in publishing order, so a slow
subscriber never delays the publisher (which may be an OS input hook).
"""

import queue
import threading
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Optional
from typing import Protocol

from tapper.feedback.logger import log

SubscribedFunction = Callable[[Any], Optional[bool]]
"""
If return value is False, the function is unsubscribed.
"""

_subscribers: dict[str, list[SubscribedFunction]] = dict()
_published: queue.Queue[tuple[str, Any]] = queue.Queue()


def subscribe(topic: str, subscribed_function: SubscribedFunction) -> None:
    """Subscribes a function to messages from a topic.

    :param topic: predefined string
    :param subscribed_function: function that will receive messages.
        It has to accept one parameter, and should be compatible
        with publisher's message' data type.
    """
    if topic not in _subscribers:
        _subscribers[topic] = []
    if subscribed_function not in _subscribers[topic]:
        _subscribers[topic].append(subscribed_function)


def unsubscribe(topic: str, subscribed_function: SubscribedFunction) -> None:
    """Unsubscribes a function to stop receiving messages from a topic.

    :param topic: same as subscribed.
    :param subscribed_function: the same function that was subscribed.
    """
    if subscribed_function in _subscribers[topic]:
        _subscribers[topic].remove(subscribed_function)


def publish(topic: str, message: Any) -> None:
    """Publishes any data as message. Returns before subscribers are called.

    :param topic: predefined string
    :param message: Any data type, dataclass of this
        should in a separate module to decouple from subscribers.
    """
    if _subscribers.get(topic):
        _published.put((topic, message))


def join() -> None:
    """Blocks until every message published so far has been delivered."""
    _published.join()


def _deliver() -> None:
    while True:
        topic, message = _published.get()
        for subscribed_function in list(_subscribers.get(topic, [])):
            try:
                if subscribed_function(message) is False:
                    unsubscribe(topic, subscribed_function)
            except Exception:
                log.warning(
                    f"Subscriber {subscribed_function} failed on '{topic}'",
                    exc_info=True,
                )
        _published.task_done()


threading.Thread(target=_deliver, name="tapper-events", daemon=True).start()


class EventDatatype(Protocol):
    """Couples data type and topic name"""

    topic: ClassVar[str]
