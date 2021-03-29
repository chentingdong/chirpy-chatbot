import os
from datetime import datetime
import logging
from python_utils.kafka_handler import KafkaHandler
from python_utils.kafka_handler import KafkaClient
from python_utils.config import logging_config
import json


class TestKafkaHandler():

    """
    Testing kafka logging handler
    """
    backup_file = logging_config['handlers']['kafka']['backup_file']
    brokers = logging_config['handlers']['kafka']['brokers']
    topic = logging_config['handlers']['kafka']['topic']
    batch_size = logging_config['handlers']['kafka']['batch_size']
    datetime_format = logging_config['formatters']['verbose']['datefmt']
    handler = KafkaHandler(backup_file, brokers, topic, batch_size)

    def test_emit(self):
        """
        test logging to kafka
        """
        logger = logging.getLogger('kafka')
        logger.addHandler(self.handler)
        logger.setLevel(logging.INFO)

        record = json.dumps({
            'timestamp':  datetime.utcnow().strftime(self.datetime_format),
            'msg': 'Unit test KafkaLoggingHandler emit method.'
        })

        logger.info(record)
        assert 1, 'should pass'

    def test_write_backup(self):
        """
        when kafka is down, handler should be able to write to backup file
        """

        record = json.dumps({
            'timestamp':  datetime.utcnow().strftime(self.datetime_format),
            'msg': 'Test kafka logging handler backup file.'
        })

        s1 = os.stat(self.backup_file).st_size
        self.handler.write_backup(record)
        self.handler.fail_fh.close()
        s2 = os.stat(self.backup_file).st_size
        assert s2>s1, 'should wrote something to backup log file {}'.format(self.backup_file)


# @pytest.mark.skip(reason='developing...')
class TestKafkaClient():
    brokers = logging_config['handlers']['kafka']['brokers']
    topic = logging_config['handlers']['kafka']['topic']

    def test_get_offsets(self):
        client = KafkaClient(self.brokers, self.topic)
        offsets_responses = client.get_offsets()

        for r in offsets_responses:
            print("partition = %s, offset = %s" % (r.partition, r.offsets[0]))

