from typing import Any

import pytest
from tapper.util import event


class Subscriber:
    received_messages: list[Any]

    def __init__(self) -> None:
        self.received_messages = list()

    def receive_message(self, sub_message: Any) -> bool:
        self.received_messages.append(sub_message)
        return self.is_unsub(sub_message)

    def is_unsub(self, message: Any) -> bool:
        return True


topic_name = "test_topic"


@pytest.mark.parametrize("message", [("a", True), 123, ("lmb", "DOWN")])
def test_pubsub(message: Any) -> None:
    subscriber = Subscriber()
    event.publish("non-existing topic doesn't break anything", 12345)
    event.subscribe(topic_name, subscriber.receive_message)
    event.publish(topic_name, message)
    event.unsubscribe(topic_name, subscriber.receive_message)
    event.publish(topic_name, "new message")

    assert subscriber.received_messages == [message]


def test_auto_unsub() -> None:
    def unsub(message: Any) -> bool:
        return message != ("b", True)

    subscriber = Subscriber()
    subscriber.is_unsub = unsub

    event.subscribe(topic_name, subscriber.receive_message)
    [
        event.publish(topic_name, m)
        for m in [("a", True), ("a", False), ("b", True), ("b", False)]
    ]

    assert subscriber.received_messages == [("a", True), ("a", False), ("b", True)]
