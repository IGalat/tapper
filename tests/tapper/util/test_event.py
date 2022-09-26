from typing import Any

import hypothesis
from hypothesis import strategies as st
from tapper.util import event


class Subscriber:
    received_message: Any

    def receive_message(self, sub_message: Any) -> None:
        self.received_message = sub_message


@hypothesis.given(st.integers() | st.text() | st.datetimes())
@hypothesis.settings(max_examples=20)
def test_pubsub(message: Any) -> None:
    subscriber = Subscriber()
    event.subscribe("topic_name", subscriber.receive_message)
    event.publish("topic_name", message)

    assert subscriber.received_message == message
