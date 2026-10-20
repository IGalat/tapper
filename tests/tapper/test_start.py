import threading
from unittest.mock import MagicMock

import pytest

import tapper
from tapper.boot import initializer
from tapper.controller import flow_control
from tapper.helper import controls


def test_terminate_makes_start_tear_down_and_return(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = MagicMock()
    monkeypatch.setattr(tapper, "_runtime", runtime, raising=False)
    monkeypatch.setattr(flow_control, "initialized", True)
    monkeypatch.setattr(tapper, "_blocking", True)
    monkeypatch.setattr(initializer, "start", MagicMock())
    stop = MagicMock()
    monkeypatch.setattr(initializer, "stop", stop)
    flow_control.shutdown.clear()

    started = threading.Thread(target=tapper.start)
    started.start()
    controls.terminate()
    started.join(timeout=0.5)

    assert not started.is_alive()
    stop.assert_called_once_with(runtime)
