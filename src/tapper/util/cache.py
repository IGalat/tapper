import functools
import weakref
from typing import Any
from typing import Callable

Fn = Callable[[Any], Any]


def lru_cache(maxsize: int = 128, typed: bool = False) -> Fn:
    """Works with unhashable types.
    https://medium.vaningelgem.be/how-to-cache-a-method-of-an-unhashable-type-in-python-5669c5daa952
    """

    def decorator(func: Fn) -> Fn:
        @functools.wraps(func)
        def wrapped_func(self: Any, *args: Any, **kwargs: Any) -> Fn:
            self_weak = weakref.ref(self)

            @functools.wraps(func)
            @functools.lru_cache(maxsize=maxsize, typed=typed)
            def cached_method(*args: Any, **kwargs: Any) -> Fn:
                return func(self_weak(), *args, **kwargs)

            setattr(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)

        return wrapped_func

    if callable(maxsize) and isinstance(typed, bool):
        # The user_function was passed in directly via the maxsize argument
        func, maxsize = maxsize, 128
        return decorator(func)

    return decorator
