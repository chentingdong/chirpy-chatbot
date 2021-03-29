# importing this module will connect to the default redis once
from redis import StrictRedis
from rediscluster import StrictRedisCluster
from python_utils.logger import logger_console
from python_utils.config import server_config

connections = dict()


def get_redis(redis_config_key='redis'):
    if redis_config_key in connections:
        return connections[redis_config_key]
    else:
        host = server_config[redis_config_key]['host']
        port = server_config[redis_config_key]['port']
        logger_console.debug('redis host {}, port {}'.format(host, port))

        is_cluster = server_config[redis_config_key].get('is_cluster', False)

        if is_cluster:
            startup_nodes = [{"host": host, "port": str(port)}]

            _redis = StrictRedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=False,
                skip_full_coverage_check=True)
        else:
            _redis = StrictRedis(
                host=host, port=port, db=0
            )

        connections[redis_config_key] = _redis
        return _redis


redis = get_redis('redis')

