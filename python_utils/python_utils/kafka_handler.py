import queue
from datetime import datetime
from pykafka import KafkaClient
import logging
import codecs
import atexit


class KafkaHandler(logging.Handler):
    """
    logging handler for producing record into kafka.
    log to backup file if kafka connection is down.
    """
    logger_console = logging.getLogger('console')
    no_connection = False

    def __init__(self, backup_file, brokers, topic, batch_size, **kwargs):
        logging.Handler.__init__(self)

        self.key = kwargs.get('key', None)
        self.fail_fh = open(backup_file, 'a+')
        self.batch_size = batch_size
        try:
            self.kafka_client = KafkaClient(brokers, socket_timeout_ms=3000)
            self.kafka_topic = self.kafka_client.topics[codecs.encode(topic)]
            self.producer = self.kafka_topic.get_producer(
                delivery_reports=True,
                min_queued_messages=batch_size,
                max_queued_messages=batch_size * 1000,
                linger_ms=1000,
                block_on_queue_full=False)
            atexit.register(lambda p: p.stop() if p._running else None, self.producer)
        except Exception as e:
            self.logger_console.error("Cannot initiate kafka connection, writting to backup file: {}".format(e))
            self.no_connection = True

        self.count = 0

    def emit(self, record):
        """
        This method receives logs as parameter record through
        logging framework, send them to Kafka Cluster
        """
        if self.no_connection:
            self.logger_console.warning("No connection to kafka.")
            self.write_backup(record)

        try:
            msg = self.format(record).encode('utf-8')

            self.producer.produce(msg, partition_key=self.key)
            # Check on delivery reports
            self.count += 1
            if self.count > (self.batch_size * 2):
                self.check_delivery()
                self.count = 0
        except AttributeError as e:
            self.logger_console.error(e)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            # TODO: reconnect is needed here.
            self.logger_console.error(e)

    def check_delivery(self):
        """Checks the delivery reports from Kafka producer,
        failed reported will be written to backup file.
        """
        while True:
            try:
                msg, exc = self.producer.get_delivery_report(block=False)
                if exc is not None:
                    self.write_backup(msg)
                    self.write_backup(repr(exc))

                    t = datetime.utcnow()
                    self.logger_console.warning("[{}]: Lost connection to kafka, writing messages to kafka backup file.".format(t))
            except queue.Empty:
                break

    def write_backup(self, msg):
        self.fail_fh.write("{}\n".format(msg))

    def close(self):
        self.fail_fh.close()

        if hasattr(self, 'producer') and self.producer:
            self.producer.stop()
