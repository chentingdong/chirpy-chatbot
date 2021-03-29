import pytest
import os
from datetime import datetime
import json
from python_utils.config import logging_config
from python_utils.logger import logger, logger_file, logger_console, logger_kafka, logger_kafka_error
from flask import url_for


class TestLoggers():
    """
    Class to group the logger testing cases.
    """
    datetime_format = logging_config['formatters']['verbose']['datefmt']

    def test_file_logger(self):
        access_log = logging_config['handlers']['file']['filename']

        s1 = os.stat(access_log).st_size
        logger_file.info('Unit test logger to file')
        s2 = os.stat(access_log).st_size
        assert s2 > s1, 'should logged something to file'

    def test_console_logger(self):
        logger_console.info('Unit test logger to console')
        assert 1, 'should pass'

    def test_kafka_logger(self):
        record = {
            'timestamp': datetime.utcnow().strftime(self.datetime_format),
            'msg': 'Unit test logger to kafka.'
        }
        msg = json.dumps(record)

        logger_kafka.info(msg)
        assert 1, 'should pass'

    def test_kafka_error_logger(self):
        record = {
            'timestamp': datetime.utcnow().strftime(self.datetime_format),
            'msg': 'Unit test logger to kafka_error.'
        }
        msg = json.dumps(record)

        logger_kafka_error.info(msg)
        assert 1, 'should pass'


class TestDecorators():

    def test_exception_decorator(self):
        """
        zero_devide() function generate an exception,
        it should be caught by decorator and log to file
        """

        @logger.exception('file')
        def zero_devide():
            print(1/0)

        assert 1, 'should pass.'

    def test_api_access_decorator_1(self, app, conversation):
        """
        api_test simulate a api call, decorated by api_access.
        which catch the request/response info and logs to logger file.
        """
        client = app.test_client()
        response = client.post(
            url_for('api_200'),
            data=json.dumps(conversation),
            content_type='application/json'
        )

        assert response.status_code == 200, 'POST test should pass.'

    def test_api_access_decorator_2(self, app):
        """
        health check
        """
        client = app.test_client()
        response = client.get(
            url_for('health_check')
        )

        assert response.status_code == 200, 'health check GET should pass.'

    def test_api_access_decorator_3(self, app, conversation):
        """
        negative test on 405 METHOD NOT ALLOWED
        """
        client = app.test_client()
        response = client.get(
            url_for('api_401'),
            data=json.dumps(conversation),
            content_type='application/json'
        )

        assert response.status_code == 405, 'Api only support POST, should fail on GET.'

