# encoding=utf-8

""" =========================== 将当前路径及工程的跟目录添加到路径中 ============================ """
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = curPath[:curPath.find("MoDeng\\")+len("MoDeng\\")]  # 获取myProject，也就是项目的根路径

sys.path.append('..')
sys.path.append(rootPath)



# from Config.GlobalSetting import g_total_stk_info_mysql
from SDK.DBOpt import genDbConn
from SDK.MyTimeOPT import get_current_datetime_str
from SDK.StkSub import getNameByStkCode
import pandas as pd

"""
本脚本用于记录操作历史

主要的命令有：

1、买卖命令：

例子： 

300508 buy 300 13.25        stk300508已经以13.25的价格买入了300股
002456 sale 200 15.3        stk002456已经以15.3的价格卖出了200股

2、查询命令
last  buy                   查询最后一次买入（未抵消）的价格

3、删除命令
del 300508 buy 300 13.25

"""

"""
数据库信息
库名：stk_opt_info

表名：history      历史的操作

stk_code stk_name amount price opt input_time reap_flag id(主键)


表名：now          持有的stk中最后买入的（已经对消过的）
stk_code stk_name amount price opt input_time


"""


def update_table_now(con, engine):

    # 读取history表
    sql_select = "SELECT * FROM history WHERE reap_flag =FALSE AND opt='buy';"
    df = pd.read_sql(con=con, sql=sql_select)

    if df.empty:
        cur=con.cursor()
        cur.execute('DELETE FROM now')
        con.commit()
        cur.close()

    else:

        df_group = list(df.groupby(by='stk_code'))
        df_latest = pd.concat(list(map(lambda x: x[1].sort_values(by='input_time', ascending=False).head(1), df_group)))

        df_latest.to_sql(con=engine, name='now', if_exists='replace',  index=False)


""" =========================== 链接数据库 ============================ """
# 新方式：lacalDBInfo包括除了“数据库名”之外的其他参数
localDBInfo = {'host': 'localhost',
               'port': 3306,
               'user': 'root',
               'password': 'myDBpassword',
               'charset': 'utf8'}

db_name = 'stk_opt_info'

table_history = 'history'
table_now = 'now'

(conn_opt, engine_opt) = genDbConn(localDBInfo, db_name)
cur = conn_opt.cursor()


""" ============================ 命令行输入逻辑 =================================== """
while True:
    input_str = input('输入你的命令：')

    # 按空格解析命令
    input_split = input_str.split(' ')

    if len(input_split) == 4:       # 插入命令

        sql_str_no_reap = 'insert into ' +\
            table_history + ' (stk_code, stk_name, amount, price, opt, input_time, reap_flag) values(' + \
            "'" + input_split[0] + "'" + ',' + \
            "'" + getNameByStkCode(g_total_stk_info_mysql, input_split[0]) + "'" + ',' + \
            str(input_split[2]) + ',' + \
            str(input_split[3]) + ',' + \
            "'" + str(input_split[1]) + "'" + ',' + \
            "'" + get_current_datetime_str() + "'" + ',' + \
            "false" + \
            ');'

        sql_str_reap = 'insert into ' +\
            table_history + ' (stk_code, stk_name, amount, price, opt, input_time, reap_flag) values(' + \
            "'" + input_split[0] + "'" + ',' + \
            "'" + getNameByStkCode(g_total_stk_info_mysql, input_split[0]) + "'" + ',' + \
            str(input_split[2]) + ',' + \
            str(input_split[3]) + ',' + \
            "'" + str(input_split[1]) + "'" + ',' + \
            "'" + get_current_datetime_str() + "'" + ',' + \
            "true" + \
            ');'

        """
        300508 buy 300 13.25

        插入数据命令insert into history (stk_code, stk_name, amount, price, opt, input_time) values('300508, "东软载波", 300, 12.34, 'buy', '2018-09-12 12:23:22');
        
        """

        # 如果是sale命令，进行抵消操作
        if input_split[1] == 'sale':

            try:
                # 查询最后一个没有被抵消的buy操作
                sql_str = "SELECT * FROM history WHERE opt='buy' AND reap_flag=FALSE AND stk_code=" + "'" + input_split[0] + "'" + " ORDER BY input_time DESC LIMIT 1;"
                df = pd.read_sql(con=conn_opt, sql=sql_str)

                if not df.empty:

                    # 取出上次买入的价格
                    price = df.loc[0, 'price']
                    id = df.loc[0, 'id']

                    # 计算营收
                    print('本次操作 earn：' + str(int(input_split[2])*(float(input_split[3]) - price)))

                    # 注销上次buy操作
                    sql_set_reap_flag = "UPDATE history SET reap_flag=true WHERE id = " + str(id) + ";"
                    cur.execute(sql_set_reap_flag)

                    # 本次卖出亦注销
                    cur.execute(sql_str_reap)
                    print('插入卖出数据成功！' + input_str + '\n并成功抵消上次buy！' + '\n' + str(df))
                    conn_opt.commit()
                else:
                    cur.execute(sql_str_no_reap)
                    print('插入卖出数据成功！无上次buy可以抵消！' + input_str)
                    conn_opt.commit()

                # 更新now表
                update_table_now(con=conn_opt, engine=engine_opt)

            except:
                print('插入卖出数据失败！')

        elif input_split[1] == 'buy':
            try:
                cur.execute(sql_str_no_reap)
                print('插入买入数据成功！' + input_str)
                conn_opt.commit()

                # 更新now表
                update_table_now(con=conn_opt, engine=engine_opt)
            except:
                print('插入买入数据失败！未知错误！')
        else:
            print('未知的操作类型：'+input_split[1])

    elif len(input_split) == 1:
        if (input_split[0] == 'exit()') | (input_split[0] == 'exit'):
            conn_opt.close()
            exit(0)
        elif input_split[0] == 'help':

            help_str = """
            1、买卖命令：
            300508 buy 300 13.25        stk300508已经以13.25的价格买入了300股
            002456 sale 200 15.3        stk002456已经以15.3的价格卖出了200股
            
            2、查询命令
            last  buy                   查询最后一次买入（未抵消）的价格
            
            3、删除命令
            del 300508 buy 300 13.25
            """
            print(help_str)

        elif input_split[0] == 'now':
            (conn_opt_now, engine_opt) = genDbConn(localDBInfo, db_name)
            df = pd.read_sql(con=conn_opt_now, sql='select * from now')
            print(str(df))
            conn_opt_now.close()


