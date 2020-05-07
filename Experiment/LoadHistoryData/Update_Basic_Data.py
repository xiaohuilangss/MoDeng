# encoding = utf-8
import tushare as ts

from Config.GlobalSetting import conn_profit, stk_profit_data_db_name, engine_profit, engine_growth, \
    stk_growth_data_db_name, stk_operation_data_db_name, stk_debtpaying_data_db_name, stk_cashflow_data_db_name, \
    engine_operation, engine_debtpaying, engine_cashflow
from sdk.DBOpt import *
from sdk.MyTimeOPT import *
year_now = get_current_date_str().split("-")[0]


def update_single_basic_ele(ele_name,retry_times):
    for year in range(2001,int(year_now)+1):
        for quarter in range(1,5):
            table_name = ele_name + str(year)+'0'+str(quarter)

            if not is_table_exist(conn=conn_profit,database_name=stk_profit_data_db_name,table_name=table_name):

                """失败达到一定次数便不再尝试"""
                failure_time = 0
                go_on_flag = True
                while go_on_flag & (failure_time < retry_times):
                    try:
                        if ele_name == "profit":
                            ts.get_profit_data(year=year,quarter=quarter)\
                                .to_sql(con=engine_profit,
                                        name=table_name,
                                        if_exists='append',
                                        schema=stk_profit_data_db_name,
                                        index=False)

                        elif ele_name == "growth":
                            ts.get_growth_data(year=year, quarter=quarter) \
                                .to_sql(con=engine_growth,
                                        name=table_name,
                                        if_exists='append',
                                        schema=stk_growth_data_db_name,
                                        index=False,)

                        elif ele_name == "operation":
                            ts.get_operation_data(year=year, quarter=quarter) \
                                .to_sql(con=engine_operation,
                                        name=table_name,
                                        if_exists='append',
                                        schema=stk_operation_data_db_name,
                                        index=False)

                        elif ele_name == "debtpaying":
                            ts.get_debtpaying_data(year=year, quarter=quarter) \
                                .to_sql(con=engine_debtpaying,
                                        name=table_name,
                                        if_exists='append',
                                        schema=stk_debtpaying_data_db_name,
                                        index=False)

                        elif ele_name == "cashflow":
                            ts.get_cashflow_data(year=year, quarter=quarter) \
                                .to_sql(con=engine_cashflow,
                                        name=table_name,
                                        if_exists='append',
                                        schema=stk_cashflow_data_db_name,
                                        index=False)

                        go_on_flag = False
                    except:
                        print(table_name+"下载失败！重试！\n")
                        failure_time = failure_time + 1
            else:
                print(table_name+"已经存在！\n")


# 更新基本面数据
for ele in ["profit","growth","operation","debtpaying","cashflow"]:
    update_single_basic_ele(ele, 6)