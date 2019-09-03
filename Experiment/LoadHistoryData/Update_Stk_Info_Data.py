# coding = utf-8

from Config.GlobalSetting import *

''' Judge whether the table for total stk info exist,
if it does ,then judge if there is some change from new to old
if doesn't ,download total stk information and save it into a mysql table '''
'''
若不存在，新下载！
若存在，判断与新的size是否一样，不一样，进行更新！
'''
if not is_table_exist(conn_basic, stk_k_data_db_name, total_stk_info_table_name):
    ts.get_stock_basics().reset_index(drop=False).to_sql(name=total_stk_info_table_name, con=engine_basic, if_exists='replace', index=True)
else:
    total_stk_info_mysql = get_total_table_data(conn_basic, total_stk_info_table_name)

    total_stk_info_internet = ts.get_stock_basics()

    if total_stk_info_internet.size != total_stk_info_mysql.size:
        total_stk_info_internet.reset_index(drop=False).to_sql(name=total_stk_info_table_name, con=engine_basic, if_exists='replace', index=True)



