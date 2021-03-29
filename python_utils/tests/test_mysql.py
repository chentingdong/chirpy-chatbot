from python_utils import mysql


def test_mysql():
    print(mysql.to_df('select * from agents where id=10', db='luke'))
    print(mysql.to_df('select * from agents where id=%(id)s', params={'id': 10}, db='luke'))