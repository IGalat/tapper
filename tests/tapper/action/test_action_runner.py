import functools
import time
from concurrent.futures import Future
from typing import Any

import hypothesis
import hypothesis.strategies as st
import pytest
from hypothesis import given
from tapper.action import runner
from tapper.action.runner import ActionRunner
from tapper.action.runner import ActionRunnerImpl
from tapper.util import datastructs


def all_actions_done(runnables: list[list[Future[Any]]]) -> bool:
    runnables = datastructs.to_flat_list(runnables)
    return not runner.prune_done_runnables(runnables)


class TestActionRunnerImpl:
    @pytest.fixture(scope="class")
    def simple_runner(self) -> ActionRunner:
        """Created once and reused. Do not mutate."""
        return ActionRunnerImpl([1])

    def test_init(self, simple_runner: ActionRunner) -> None:
        config_value = [10, 20, 1, 30]
        runner_ = ActionRunnerImpl(config_value)
        assert len(runner_.executors) == len(config_value)
        assert runner_.ex_threads == config_value

    def test_simplest_run(self, simple_runner: ActionRunner) -> None:
        result = 0

        def increment() -> None:
            nonlocal result
            result += 1

        simple_runner.run(increment)
        assert result == 1

    @given(exec_number=st.integers(min_value=1))
    def test_run_in_nonexistent_executor(
        self, simple_runner: ActionRunner, exec_number: int
    ) -> None:
        with pytest.raises(IndexError):
            simple_runner.run(lambda: "q", exec_number)

    def test_none_action(self, simple_runner: ActionRunner) -> None:
        # noinspection PyTypeChecker
        simple_runner.run(None)

    def test_exception_in_action(self, simple_runner: ActionRunner) -> None:
        def throw() -> None:
            raise UnicodeError

        simple_runner.run(throw)

    @given(q=st.integers(min_value=1, max_value=500))
    @hypothesis.settings(max_examples=10)
    def test_no_queue_for_1_thread(self, q: int) -> None:
        runner_ = ActionRunnerImpl([1])
        result = 0

        def increment() -> None:
            nonlocal result
            time.sleep(0.001)
            result += 1

        [runner_.run(increment) for _ in range(q)]
        while not all_actions_done(runner_._runnables):
            time.sleep(0.001)
        assert result == 1

    @given(
        matrix=st.integers(min_value=1, max_value=10).flatmap(  # number of executors
            lambda exc: st.tuples(
                st.lists(  # threads in each executor
                    st.integers(min_value=1, max_value=40), min_size=exc, max_size=exc
                ),
                st.lists(  # actions thrown at each executor
                    st.integers(min_value=1, max_value=50), min_size=exc, max_size=exc
                ),
            )
        )
    )
    @hypothesis.settings(max_examples=5)
    def test_many_execs_parallel(self, matrix: list[list[int]]) -> None:
        """Example: exec_threads = [5, 1, 17], actions_quantity [2, 48, 23]
        expected result [2, 1, 17]"""
        exec_threads, actions_quantity = matrix
        expected = [
            min(exec_threads[i], actions_quantity[i]) for i in range(len(exec_threads))
        ]

        runner_ = ActionRunnerImpl(exec_threads)
        result = [0] * len(exec_threads)

        def increment(ordinal: int) -> None:
            nonlocal result
            # Lower sleep time sometimes leads to test failure.
            # It may take as long as 0.04s on my machine to launch all functions
            time.sleep(0.1)
            result[ordinal] += 1

        for action_n in range(max(actions_quantity)):
            for ex_ord in range(len(exec_threads)):
                if actions_quantity[ex_ord] > action_n:
                    runner_.run(functools.partial(increment, ex_ord), ex_ord)

        while not all_actions_done(runner_._runnables):
            time.sleep(0.01)
        assert expected == result
