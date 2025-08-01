from collections.abc import AsyncGenerator, AsyncIterator, Coroutine, Generator
from typing import Callable, TypeVar, Union

# A placeholder type variable representing whatever type a dependency callable returns.
# This makes DependencyCallable generic over its return type.
RETURN_TYPE = TypeVar("RETURN_TYPE")


# A generic type for FastAPI dependency functions or callables.
# It covers:
#   1. Synchronous functions returning RETURN_TYPE
#   2. Asynchronous functions (`async def`) returning RETURN_TYPE
#   3. Generator-based dependencies (sync or async) that yield RETURN_TYPE
#
# By using `Callable[..., Union[...]]`, we allow any parameters (the `...`)
# and unify all valid FastAPI dependency return styles under one alias.
DependencyCallable = Callable[
    ...,
    Union[
        RETURN_TYPE,
        Coroutine[None, None, RETURN_TYPE],
        AsyncGenerator[RETURN_TYPE, None],
        Generator[RETURN_TYPE, None, None],
        AsyncIterator[RETURN_TYPE],
    ],
]
