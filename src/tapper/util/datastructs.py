"""Data structures transform"""
from typing import Any
from typing import Iterable
from typing import Sequence


def to_flat_list(data_structure: Sequence[Any] | Any) -> list[Any]:
    """Transforms single values to list; flattens to list any (nested too) Sequence."""
    return list(_flatten(data_structure))


def _flatten(xs: Sequence[Any]) -> Iterable[Any]:
    if isinstance(xs, Sequence) and not isinstance(xs, (str, bytes)):
        for x in xs:
            if isinstance(x, Sequence) and not isinstance(x, (str, bytes)):
                yield from _flatten(x)
            else:
                yield x
    else:
        yield xs
