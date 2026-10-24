import functools
import weakref
from collections.abc import Callable
from typing import Concatenate
from typing import overload


@overload
def lru_cache[S, **P, R](
    func: Callable[Concatenate[S, P], R], /
) -> Callable[Concatenate[S, P], R]: ...


@overload
def lru_cache[S, **P, R](
    *, maxsize: int = 128, typed: bool = False
) -> Callable[[Callable[Concatenate[S, P], R]], Callable[Concatenate[S, P], R]]: ...


def lru_cache[S, **P, R](
    func: Callable[Concatenate[S, P], R] | None = None,
    /,
    *,
    maxsize: int = 128,
    typed: bool = False,
) -> (
    Callable[Concatenate[S, P], R]
    | Callable[[Callable[Concatenate[S, P], R]], Callable[Concatenate[S, P], R]]
):
    """functools.lru_cache for methods of unhashable types: the cache lives on the instance
    and holds only a weak reference to it, so instances are not kept alive by their cache.
    https://medium.vaningelgem.be/how-to-cache-a-method-of-an-unhashable-type-in-python-5669c5daa952
    """

    def decorator(
        func: Callable[Concatenate[S, P], R],
    ) -> Callable[Concatenate[S, P], R]:
        @functools.wraps(func)
        def wrapped_func(self: S, *args: P.args, **kwargs: P.kwargs) -> R:
            self_weak = weakref.ref(self)

            @functools.wraps(func)
            @functools.lru_cache(maxsize=maxsize, typed=typed)
            def cached_method(*args: P.args, **kwargs: P.kwargs) -> R:
                self_ = self_weak()
                assert self_ is not None  # only reachable through a live `self`
                return func(self_, *args, **kwargs)

            setattr(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)

        return wrapped_func

    return decorator if func is None else decorator(func)
