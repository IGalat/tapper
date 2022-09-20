""" Publisher-subscriber implementation.

    Typical usage example:

    To subscribe:
        event.subscribe(PREDEFINED_TOPIC_NAME, function_that_will_receive_messages)
    (can be done in a different place than the subscriber)

    In publisher:
        event.publish(PREDEFINED_TOPIC_NAME, message_of_any_type)
"""
from typing import Any
from typing import Callable

SubscribedFunction = Callable[[Any], None]

_subscribers: dict[str, list[SubscribedFunction]] = dict()


def subscribe(topic: str, subscribed_function: SubscribedFunction) -> None:
    """Subscribes a function to messages from a topic

    :param topic: predefined string
    :param subscribed_function: function that will receive messages.
        It has to accept one parameter, and should be compatible
        with publisher's message' data type
    """
    if topic not in _subscribers:
        _subscribers[topic] = []
    _subscribers[topic].append(subscribed_function)


def publish(topic: str, message: Any) -> None:
    """Publishes any data as message

    :param topic: predefined string
    :param message: Any data type, dataclass of this
        should in a separate module to decouple from subscribers
    """
    if topic not in _subscribers:
        return
    for subscribed_function in _subscribers[topic]:
        subscribed_function(message)
