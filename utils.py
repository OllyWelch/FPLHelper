import functools
import time


def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        print("Executing {}".format(func.__name__))
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print("Finished {} in {} secs.".format(func.__name__, round(run_time, 4)))
        return value
    return wrapper_timer
