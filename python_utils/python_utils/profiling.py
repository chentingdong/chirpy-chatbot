import time
from python_utils.logger import logger_console


def log_time(method):
    def timed(*args, **kw):
        t1 = time.time()
        result = method(*args, **kw)
        t2 = time.time()
        arg_name = None
        if args:
            arg_name = getattr(args[0], 'name', None)
        logger_console.debug("{} of '{}' took {} seconds".format(method.__qualname__, arg_name, round(t2 - t1, 3)))
        return result
    return timed