import functools
import threading
from concurrent.futures import wait
from typing import Any

import hypothesis
import hypothesis.strategies as st
import pytest
from hypothesis import given

from tapper.action.runner import ActionRunner
from tapper.action.runner import ActionRunnerImpl
from tapper.util import datastructs


@st.composite
def executor_loads(draw: st.DrawFn) -> list[tuple[int, int]]:
    """Per executor: how many threads it has, and how many actions get thrown at it."""
    executors = draw(st.integers(min_value=1, max_value=10))
    threads = st.integers(min_value=1, max_value=40)
    actions = st.integers(min_value=1, max_value=50)
    return draw(
        st.lists(st.tuples(threads, actions), min_size=executors, max_size=executors)
    )


def assert_runner_still_runs(runner_: ActionRunnerImpl) -> None:
    """The previous action has finished, however it ended, and a new one goes through."""
    wait_all(runner_)
    ran: list[int] = []
    runner_.run(functools.partial(ran.append, 1))
    wait_all(runner_)
    assert ran == [1]


def accepted(runner_: ActionRunnerImpl) -> list[int]:
    """How many actions each executor took on."""
    return [len(futures) for futures in runner_._runnables]


def wait_all(runner_: ActionRunnerImpl) -> None:
    wait(datastructs.to_flat_list(runner_._runnables))


class TestShutdown:
    def test_waits_for_actions_that_finish_in_time(self) -> None:
        runner_ = ActionRunnerImpl([1])
        runner_.run(lambda: None)
        wait_all(runner_)
        assert runner_.shutdown(timeout=1) == 0

    def test_reports_actions_still_running(self) -> None:
        runner_ = ActionRunnerImpl([1])
        gate = threading.Event()
        runner_.run(gate.wait)
        assert runner_.shutdown(timeout=0.01) == 1
        gate.set()


class TestActionRunnerImpl:
    @pytest.fixture(scope="class")
    def simple_runner(self) -> ActionRunnerImpl:
        """Created once and reused. Do not mutate."""
        return ActionRunnerImpl([1])

    def test_init(self, simple_runner: ActionRunnerImpl) -> None:
        config_value = [10, 20, 1, 30]
        runner_ = ActionRunnerImpl(config_value)
        assert len(runner_.executors) == len(config_value)
        assert runner_.ex_threads == config_value

    def test_simplest_run(self, simple_runner: ActionRunnerImpl) -> None:
        result = 0

        def increment() -> None:
            nonlocal result
            result += 1

        simple_runner.run(increment)
        wait_all(simple_runner)
        assert result == 1

    @given(exec_number=st.integers(min_value=1))
    def test_run_in_nonexistent_executor(
        self, simple_runner: ActionRunner, exec_number: int
    ) -> None:
        with pytest.raises(IndexError):
            simple_runner.run(lambda: "q", exec_number)

    def test_exception_in_action_does_not_break_the_runner(
        self, simple_runner: ActionRunnerImpl
    ) -> None:
        def throw() -> None:
            raise UnicodeError

        simple_runner.run(throw)
        assert_runner_still_runs(simple_runner)

    def test_none_action_does_not_break_the_runner(
        self, simple_runner: ActionRunnerImpl
    ) -> None:
        none_action: Any = None
        simple_runner.run(none_action)
        assert_runner_still_runs(simple_runner)

    def test_no_queue_for_1_thread(self) -> None:
        runner_ = ActionRunnerImpl([1])
        gate = threading.Event()
        for _ in range(5):
            runner_.run(gate.wait)
        assert accepted(runner_) == [1]
        gate.set()
        wait_all(runner_)

    @given(loads=executor_loads())
    @hypothesis.settings(max_examples=5)
    def test_many_execs_parallel(self, loads: list[tuple[int, int]]) -> None:
        """Each executor takes on at most as many actions as it has threads.
        Example: exec_threads = [5, 1, 17], actions_quantity [2, 48, 23],
            expected result [2, 1, 17]"""
        exec_threads = [threads for threads, _ in loads]
        expected = [min(threads, actions) for threads, actions in loads]

        runner_ = ActionRunnerImpl(exec_threads)
        gate = threading.Event()
        ran = [0] * len(exec_threads)
        counting = threading.Lock()

        def increment(ordinal: int) -> None:
            gate.wait()
            with counting:
                ran[ordinal] += 1

        for ordinal, (_, actions) in enumerate(loads):
            for _ in range(actions):
                runner_.run(functools.partial(increment, ordinal), ordinal)
        assert accepted(runner_) == expected

        gate.set()
        wait_all(runner_)
        assert ran == expected
        runner_.shutdown(timeout=1)
