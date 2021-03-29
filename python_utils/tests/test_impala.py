from python_utils.impala import impala_global


def test_execute():
    sql = 'show databases'
    result = impala_global.execute(sql)
    assert result, 'test impala.execute failed'


def test_fetchall():
    sql = 'select * from leia.neva_gold_standard'
    result = impala_global.fetchall(sql, as_dataframe=True)
    assert result is not None


def test_close():
    sql = 'show databases'

    impala_global.cursor.close()
    impala_global.conn.close()

    result = impala_global.execute(sql)
    assert result==False, 'cannot disconnect impala'


def test_reconnect():
    sql = 'show databases'

    impala_global.reconnect()

    result = impala_global.execute(sql)
    assert result==True, 'cannot reconnect impala'