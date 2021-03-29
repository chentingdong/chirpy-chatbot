from python_utils.redis_store import get_redis
from python_utils.config import server_config
from uuid import uuid4

redis_prefix = 'd:pu:test:'
value = 'test'
expire = 600


def test_set_get():
    key = redis_prefix + str(uuid4())

    redis = get_redis()

    redis.setex(key, expire, value)
    assert redis.get(key).decode('utf-8') == value


def test_key_with_pattern():
    redis = get_redis()

    pattern = redis_prefix + '*'
    records = redis.keys(pattern)
    assert isinstance(records, list)
    assert len(records) > 0


def test_stand_alone_mode():
    server_config['redis']['is_cluster'] = False
    server_config['redis']['host'] = 'localhost'
    server_config['redis']['port'] = 6379

    redis = get_redis()

    key = redis_prefix + str(uuid4())
    redis.setex(key, expire, value)

    assert redis.get(key).decode('utf-8') == value
