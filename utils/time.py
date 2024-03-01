import time
from functools import wraps


def timeit(custom_name: str | None):
    def inner(func):
        @wraps(func)
        def timeit_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            name = custom_name if custom_name is not None else f'Function {func.__name__}'
            print(f'{name} took {total_time:.4f} seconds')
            return result

        return timeit_wrapper

    return inner
