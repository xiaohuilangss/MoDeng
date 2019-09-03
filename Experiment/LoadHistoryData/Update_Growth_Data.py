# encoding = utf-8

from Config.GlobalSetting import *
from SDK.MyTimeOPT import get_current_date_str

for year in range(2002, int(get_current_date_str().split('-')[0]) + 1):
    for quarter in range(1, 5):
        table_name = 'growth' + str(year)+'0'+str(quarter)

        if not is_table_exist(conn=conn_growth,database_name=stk_growth_data_db_name,table_name=table_name):

            go_on_flag = True
            while(go_on_flag):
                try:
                    ts.get_growth_data(year=year,quarter=quarter)\
                        .to_sql(con=engine_growth,
                                name=table_name,
                                if_exists='append',
                                schema=stk_growth_data_db_name,
                                index=False)
                    go_on_flag = False
                except:
                    print("growth "+table_name+"下载失败！重试！\n")
        else:
            print("growth "+table_name+"已经存在！\n")


# 更新growth数据

