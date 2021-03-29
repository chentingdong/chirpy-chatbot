from python_utils.logger import logger_console
from python_utils.concurrent import pool_stoppable, pool_runner
import time
import random


@pool_stoppable
def bomb(*args):
    time.sleep(random.random())
    logger_console.debug("args={}".format(args))
    if args[0] == 5:
        raise Exception("bomb exploded")
    return args[0] + 1


if __name__ == "__main__":
    try:
        results = pool_runner(2, bomb, [(i,) for i in range(10)], sync=False)
        logger_console.debug("Pool run results: {}".format(results))
    except Exception as e:
        logger_console.warn("Pool run failed")
