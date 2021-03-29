import logging
import logging.config
import time
import json
import sys
import traceback
import os
from datetime import datetime
from flask import request, session

from python_utils.config import logging_config
from python_utils.helpers import version, is_json


class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            serialized = json.JSONEncoder.default(self, obj)
        except Exception:
            serialized = {obj.__repr__(): "Not JSON Serializable"}
        return serialized


class Logger(object):

    def __init__(self):
        self.reinit()

    def reinit(self):
        logging.config.dictConfig(logging_config)

    def get(self, logger_name):
        return logging.LoggerAdapter(logging.getLogger(logger_name),
                                     {"ASTOUND_RELEASE_VERSION": version})

    def api_access(self, logger_name_file='file', logger_name_kafka='kafka'):
        """
        A decorator that can be used to end point for access logs and kafka logs
        :param logger_name_file: the name of the file logger
        :type logger_name_file: str
        :param logger_name_kafka: the name of the kafka logger
        :type logger_name_kafka: str
        :return: decorated function
        """
        from functools import wraps

        def decorator(api_request):
            """
            Decorating API request handling function
            :param api_request: the handling function
            :return: the decorated function
            """

            @wraps(api_request)
            @self.exception()
            def decorated(*args, **kwargs):

                _logger_file = self.get(logger_name_file)
                _logger_kafka = self.get(logger_name_kafka)

                t1 = time.time()
                ts1 = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                response = api_request(*args, **kwargs)
                t2 = time.time()
                ts2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                extra = {
                    'request_url': request.url or '',
                    'response_status': response.status or '',
                    'response_latency': t2-t1 or 0,
                    'request_size': request.content_length or 0,
                    'response_size': sys.getsizeof(response) or 0
                }

                msg = ''.join(['{}: {}, '.format(key, extra[key]) for key in sorted(extra)])

                _logger_file.info(msg)

                self.session_run_time()

                if is_json(response.get_data().decode('utf-8')):
                    data_payload = json.loads(response.get_data().decode('utf-8'))
                else:
                    data_payload = ''

                kafka_msg = {
                    "request": {
                        'ip': request.remote_addr,
                        "url": request.url,
                        "method": request.method,
                        "view_args": request.view_args,
                        "args": request.args.to_dict(),
                        "headers": dict(request.headers.items()),
                        "json": request.get_json(silent=True) or {},
                        "ts": ts1
                    },
                    "response": {
                        "status": response.status,
                        "data": data_payload,
                        "ts": ts2,
                        "headers": dict(response.headers.items())
                    },
                    "session_data": session.get('data', {})
                }

                _logger_kafka.info(json.dumps(kafka_msg, cls=SafeJSONEncoder))

                return response

            return decorated
        return decorator

    def exception(self, where=None):
        """
        A decorator that wraps the passed in function and logs exceptions
        :param where: indicates the logger
        :type where: str
        """
        if where is None:
            where = 'console'

        _logger = self.get(where)

        from functools import wraps

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    response = func(*args, **kwargs)
                    return response
                except Exception as e:
                    err = "Logger caught an exception in {}: {}".format(func.__name__, e)
                    _logger.exception(err)
                    _logger.debug(traceback.format_exc())
                    raise e

            return wrapper
        return decorator

    def composed_decorators(*decs):
        """
        compose of multiple decorators
        :param decs: dec1, dec2, ...
        :return: composed decorator
        """
        def deco(f):
            for dec in reversed(decs):
                f = dec(f)
            return f

        return deco

    def session_run_time(self):
        if 'CONFIG_ENV' in os.environ:
            release_env = os.environ.get('CONFIG_ENV', 'NotFound')
        else:
            release_env = 'NotFound'

        runtime_data = {
            'release_version': version,
            'release_env': release_env
        }

        if not session.get('data'):
            session['data'] = {}

        session['data']['runtime_data'] = runtime_data


# global object that shares in app
logger = Logger()
# log to access.log
logger_file = logger.get('file')
# log to console, if docker-compose, goes to cloudwatch
logger_console = logger.get('console')
# log to kafka
logger_kafka = logger.get('kafka')
logger_events = logger.get('events')
# log to kafka error topic
logger_kafka_error = logger.get('kafka_error')
