# coding = utf-8
import pandas as pd
import pymysql
from sqlalchemy import create_engine

''' Function:return all stk information
 :param conn                handle to database
 :param tableName           the table name of total stk info
 :return                    dataframe
 '''


def get_total_table_data(conn, table_name):

    if not any(table_name):
        return None

    if table_name[0].isdigit():                                     # if the first element in table_name is digital
        table_name_inner = '`' + table_name + '`'
    else:
        table_name_inner = table_name

    return pd.read_sql(con=conn, sql="select * from " + table_name_inner).drop_duplicates()


'''Function: judge if a table exist in the database
 :param conn                handle to database
 :param tableName           the table name of total stk info
 :return                    true ? false ?
'''
def is_table_exist(conn, database_name, table_name):
    cur = conn.cursor()
    if not any(table_name):
        return None

    result =  cur.execute('SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ' + "'" + table_name + "'" +
                       ' AND TABLE_SCHEMA = ' + "'" + database_name + "'")

    cur.close()

    return result


def is_field_exist(cur, database_name, table_name, field_name):
    if not any(table_name):
        return None

    return cur.execute('SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ' + "'" + table_name + "'" +
                       ' AND TABLE_SCHEMA = ' + "'" + database_name + "'" + "AND COLUMN_NAME = " + "'" + field_name + "'")


def insert_row_to_database(conn_param, field, value, table_name, db_name):


    """
    向数据库中添加一行（表没有，则自动添加。字段亦如此）

    :param conn_param:
    :param field:       字段，list形式
    :param value:       给相应字段赋值，list形式
    :param table_name:
    :return:
    """



    # 判断table是否存在，不存在则创建之
    cur = conn_param.cursor()
    if not is_table_exist(cur=cur, table_name=table_name, database_name=db_name):

        # 创建此表
        cur.execute('CREATE TABLE ' + table_name + ' (' + field + ' VARCHAR(40))')
        cur.execute('INSERT INTO ' + table_name + '(' + field + ') ' + ' VALUES(' + '"' + value + '"' + ')')
    else:

        # 遍历字段列表，对于表中不存在的字段，向表中自动添加
        for fd in field:
            if not is_field_exist(cur=cur,database_name=db_name,table_name=table_name,field_name=fd):
                add_columns(cur=cur,table_name=table_name,columns_name=fd)

        # 将字段list合并为字符串
        field_str = ""
        for fd in field:
            if len(field_str):
                field_str = field_str+','+fd
            else:
                field_str = field_str + fd

        # 将VALUE list整理为字符串形式
        value_str = ""
        for v in value:
            if len(value_str):
                value_str = value_str + ',' + '"' + v + '"'
            else:
                value_str = value_str  + '"' + v + '"'

        cur.execute('INSERT INTO ' + table_name + '(' + field_str + ') ' + ' VALUES(' + value_str + ')')

    cur.close()
    conn_param.commit()



def set_primary_key(conn_param, key_field, table_name, auto_increment):

    """
    使用SQL语句对表设置主键

    :param conn_param:
    :param key_field:
    :param table_name:
    :param auto_increment:
    :return:
    """


    cur = conn_param.cursor()
    if auto_increment:
        cur.execute('ALTER TABLE ' + table_name + ' MODIFY ' + key_field + ' INTEGER auto_increment')
    else:
        cur.execute('ALTER TABLE ' + table_name + ' MODIFY ' + key_field)


def add_columns(cur, table_name, columns_name):
    cur.execute('ALTER TABLE ' + table_name + ' ADD ' + columns_name + ' VARCHAR(50) ')


def genDbConn(dbInfoParam,dbNameParam):

    """
    根据数据库信息生成数据库句柄，用以操作数据库
    :param dbInfoParam:
    :param dbNameParam:
    :return:
    """

    dbTemp = {'host': dbInfoParam['host'],
                   'port': dbInfoParam['port'],
                   'user': dbInfoParam['user'],
                   'password': dbInfoParam['password'],
                   'database': dbNameParam,
                   'charset': dbInfoParam['charset']}

    engine = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % dbTemp)

    conn_tick = pymysql.connect(
        host=dbTemp['host'],
        port=dbTemp['port'],
        user=dbTemp['user'],
        passwd=dbTemp['password'],
        db=dbTemp['database'],
        charset=dbTemp['charset'])

    return (conn_tick,engine)






