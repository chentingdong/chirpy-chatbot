from sqlalchemy import pool
from python_utils.logger import logger_console
from python_utils.config import server_config
from impala.dbapi import connect
from impala.util import as_pandas
import traceback


class Impala:

    def __init__(self, impala_config=None):
        if not impala_config:
            impala_config = 'impala'

        self.conn = connect(
            host=server_config['impala']['host'],
            port=int(server_config['impala']['port']),
        )
        self.cursor = self.conn.cursor()
        self.conn_pool = pool.QueuePool(self.conn, max_overflow=10, pool_size=100, echo=True, timeout=60)

    def reconnect(self):
        logger_console.warning("Reconnecting impala...")

        self.conn = connect(
            host=server_config['impala']['host'],
            port=int(server_config['impala']['port']),
        )

        self.cursor = self.conn.cursor()

    def execute(self, query):
        logger_console.info(query)
        self.sync_ddl()

        try:
            self.cursor.execute(query)
        except Exception as e:
            logger_console.error(traceback.format_exc())
            logger_console.error("Impala connection cannot execute query: {}".format(e))
            return False
        return True

    def execute_safe(self, sql_template, sql_dict):
        """
        If query are from external, use this to avoid sql injection
        example:
        :param sql_template:
        [code]
        sql_template = "UPSERT INTO {table_name} ( field_name ) values ( %(field_name)s)"
        [/code]
        :param sql_dict:
        sql_dict = { field_name: 'something' }
        :return:
        """
        self.sync_ddl()

        try:
            self.cursor.execute(sql_template, sql_dict)
        except Exception as e:
            logger_console.error(traceback.format_exc())
            logger_console.error("Impala connection cannot execute query: {}".format(e))
            return False
        return True

    def fetchall(self, query, as_dataframe=True):
        self.sync_ddl()

        try:
            self.cursor.execute(query)
            if as_dataframe:
                return as_pandas(self.cursor)
            else:
                return self.cursor.fetchall()
        except Exception as e:
            logger_console.error(traceback.format_exc())
            logger_console.error("Impala connection cannot execute fetch all: {}".format(e))
            return False
        return True

    def sync_ddl(self):
        try:
            self.cursor.execute("set SYNC_DDL=true")
        except Exception as e:
            logger_console.error(traceback.format_exc())
            logger_console.warning("Impala connection issue on sync ddl.")
            self.reconnect()


impala_global = Impala()
