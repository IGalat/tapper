from typing import Any

import hypothesis
import strategies
from tapper.util import event


class Subscriber:
    received_message: Any

    def receive_message(self, sub_message: Any) -> None:
        self.received_message = sub_message


subscriber = Subscriber()
topic_name = "test_topic"


@hypothesis.given(strategies.primitives)
@hypothesis.settings(max_examples=20)
def test_pubsub(message: Any) -> None:
    event.publish("non-existing topic doesn't break anything", 123)
    event.subscribe(topic_name, subscriber.receive_message)
    event.publish(topic_name, message)
    event.unsubscribe(topic_name, subscriber.receive_message)
    event.publish(topic_name, "new message")

    assert subscriber.received_message is message
