"""Type checking"""
from typing import Any
from typing import TypeGuard
from typing import TypeVar

T = TypeVar("T")


def is_list_of(target: Any, values_type: type[T]) -> TypeGuard[list[T]]:
    return (
        target is not None
        and isinstance(target, list)
        and all(isinstance(x, values_type) for x in target)
    )


def is_tuple_of(target: Any, values_type: type[T]) -> TypeGuard[list[T]]:
    return (
        target is not None
        and isinstance(target, tuple)
        and all(isinstance(x, values_type) for x in target)
    )
