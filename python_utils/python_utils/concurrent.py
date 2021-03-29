from multiprocessing import Pool, Value
from functools import wraps
from python_utils.logger import logger_console
from ctypes import c_char_p


def pool_stoppable(func):
    """
    decorator for Pool functions, which stops the whole pool if func returns 0
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args):
        if stop_signal.value:
            return

        result = None
        try:
            result = func(*args)
            count_tracker.value += 1
            logger_console.info("{} Finished iteration {}".format(
                global_pool_name.value.decode('utf-8'), count_tracker.value))
        except Exception as e:
            stop_signal.value = 1
        return result

    return wrapper


def pool_runner(processes, func, iterable, initializer=None, initargs=[], sync=True, pool_name='unnamed'):
    """
    :param processes: number of parallel processes in the pool
    :param func: a pool_stoppable decorated func
    :param iterable: the elements of the iterable are expected to be iterables that are unpacked as arguments
    :param initializer: If initializer is not None then each worker process will call initializer(*initargs) when it starts.
    :param initargs:
    :return:
    """
    global count_tracker, stop_signal, global_pool_name
    count_tracker = Value('i', 0)
    stop_signal = Value('i', 0)
    total_count = len(iterable)
    global_pool_name = Value(c_char_p, pool_name.encode('utf-8'))

    results = []
    if total_count > 0:
        logger_console.info("Starting {} pool with {} iterations".format(pool_name, total_count))
        with Pool(processes=processes, initializer=initializer, initargs=initargs) as p:
            if sync:
                results = p.starmap(func, iterable)
            else:
                results = p.starmap_async(func, iterable).get()
            logger_console.debug("results={}".format(results))
        finished_count = count_tracker.value
        logger_console.info("{} Pool Summary: total count = {}, finished {}".format(
            pool_name, total_count, finished_count, stop_signal.value))

    # typecode of stop_signal is int
    if stop_signal.value > 0:
        raise Exception("Pool didn't finish completely")
    return results

