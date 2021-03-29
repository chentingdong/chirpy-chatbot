import traceback

import pymysql.cursors
from python_utils.logger import logger_console
from python_utils.config import server_config
import pandas as pd


def mysql_connect(db=None):
    mysql_config = server_config.get('mysql')

    if db:
        mysql_config = mysql_config.get(db)

    mysql_connection = pymysql.connect(host=mysql_config['host'],
                                       user=mysql_config['user'],
                                       password=mysql_config['password'],
                                       db=mysql_config['database'],
                                       charset='utf8mb4',
                                       cursorclass=pymysql.cursors.DictCursor)

    return mysql_connection


def mysql_execute(sql, params={}, db=None):
    try:
        mysql_connection = mysql_connect(db=db)
        mysql_cursor = mysql_connection.cursor()
        mysql_cursor.execute(sql, params)
        results = mysql_cursor.fetchall()
        mysql_connection.commit()
    except Exception as e:
        logger_console.error(e)
        return

    mysql_connection.close()
    return results


def fetch_org_meta(db=None):
    sql = "select * from neva_web_console.org_meta"
    results = mysql_execute(sql, db=db)
    org_meta = {}
    for org in results:
        org_id = org['org_id']
        if org_id not in org_meta:
            org_meta[org_id] = {}
        org_meta[org_id][org['meta_key']] = org['meta_value']
    return org_meta


def fetch_orgs(db=None):
    sql = "select id, name from neva_web_console.orgs"
    orgs = mysql_execute(sql, db=db)
    return orgs


def to_df(sql, params={}, db=None):
    try:
        mysql_connection = mysql_connect(db=db)
        df = pd.read_sql(sql, params=params, con=mysql_connection)
    except Exception as e:
        logger_console.error(traceback.format_exc())
        logger_console.error(e)
        return

    mysql_connection.close()
    return df

