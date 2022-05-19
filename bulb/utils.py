import functools
from typing import Callable, TypeVar, ParamSpec

T_args = ParamSpec('T_args')
T_ret = TypeVar('T_ret')


def once_init(function: Callable[T_args, T_ret]) -> Callable[T_args, T_ret]:
    cache = None
    inited = False

    @functools.wraps(function)
    def wrapper(*args: T_args.args, **kwargs: T_args.kwargs) -> T_ret:
        nonlocal inited, cache
        if not inited:
            cache = function(*args, **kwargs)
            inited = True

        return cache

    return wrapper


def once_init_async(function: Callable[T_args, T_ret]) -> Callable[T_args, T_ret]:
    cache = None
    inited = False

    @functools.wraps(function)
    async def wrapper(*args: T_args.args, **kwargs: T_args.kwargs) -> T_ret:
        nonlocal inited, cache
        if not inited:
            cache = await function(*args, **kwargs)
        inited = True

        return cache

    return wrapper
