from abc import ABC
from abc import abstractmethod
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import Final

from tapper.model import types_


class ActionRunner(ABC):
    """Runs the actions that were triggered.

    Has a number of executors, each has a number of threads.
    Action queueing is not allowed: if all of executor's threads are currently executing actions,
        request to run another action in that executor will be ignored.
    """

    @abstractmethod
    def run(self, fn: types_.Action, executor_ordinal: int = 0) -> None:
        """Runs an action.

        :param fn: action to run.
            It must require no arguments. Use `functools.partial` to provide arguments beforehand.
            The result is ignored.
        :param executor_ordinal: Which executor to run in. If not specified, will run in
            the first one (index 0).
        """

    @abstractmethod
    def run_control(self, fn: types_.Action) -> None:
        """Runs an action in a separate thread. Intended to be only used for control of tapper flow.

        There is no concurrency for this, and queueing is not allowed.
        """


def prune_done_runnables(runnables: list[Future[Any]]) -> list[Future[Any]]:
    return [r for r in runnables if not r.done()]


class ActionRunnerImpl(ActionRunner):
    executors: Final[list[ThreadPoolExecutor]]
    """Regular tasks are executed in these."""

    ex_threads: Final[list[int]]
    """Number of threads per executor. Defines how much concurrency there is."""

    control_executor: Final[ThreadPoolExecutor]
    """Executes control group actions."""

    _runnables: list[list[Future[Any]]]
    """Currently running or done tasks, per executor."""

    _control_runnable: Future[Any]
    """Currently running or done task for control executor."""

    def __init__(self, executors_threads: list[int]) -> None:
        """
        :param executors_threads: see ActionRunner doc for general explanation.
            If this is None, 1 executor with 1 thread is generated.
        """
        self.ex_threads = executors_threads
        self.executors = [
            ThreadPoolExecutor(max_workers=threads) for threads in executors_threads
        ]
        self._runnables = [[] for _ in executors_threads]

        self.control_executor = ThreadPoolExecutor(max_workers=1)

    def run(self, fn: types_.Action, executor_ordinal: int = 0) -> None:
        exc = executor_ordinal
        self._runnables[exc] = prune_done_runnables(self._runnables[exc])
        if len(self._runnables[exc]) < self.ex_threads[exc]:
            runnable = self.executors[exc].submit(fn)
            self._runnables[exc].append(runnable)

    def run_control(self, fn: types_.Action) -> None:
        if not hasattr(self, "_control_runnable") or self._control_runnable.done():
            self._control_runnable = self.control_executor.submit(fn)
