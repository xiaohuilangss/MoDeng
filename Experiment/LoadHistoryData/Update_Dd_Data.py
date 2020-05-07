# encoding = utf-8

from General.MyTimeOPT import *

from Config.GlobalSetting import *
from sdk.DBOpt import *


def get_single_day_dd_data(date_param, code, big_than=400):

    try:
        native_data_today_df = ts.get_sina_dd(code=code, date=date_param, vol=big_than)
    except:
        print('代码：' + code + ' 日期：' + date_param + ' 大单数据下载失败！')
        return {}

    # if data is empty,it would be error,when sorted by time!,so a judgement here is necessary!
    if native_data_today_df is None:
        data_today_sort_by_time = native_data_today_df
    else:
        data_today_sort_by_time = native_data_today_df.sort_values(by=["time"])

    # if there is no today's data,return a empty dictionary
    if data_today_sort_by_time is None:
        print('代码：'+code+' 日期：' + date_param + ' 没有当天数据！')
        return {}
    else:
        print('代码：' + code + ' 日期：' + date_param + ' 大单数据下载成功！')

    big = data_today_sort_by_time

    data_in = big[big.type == "买盘"]                 # 买盘的数据
    fund_in = data_in.price*data_in.volume          # 总入场资金量

    data_out = big[big.type == "卖盘"]            # 卖盘的数据
    fund_out = data_out.price*data_out.volume   # funds all out

    return {"date": date_param,
            "big_in": fund_in,
            "big_out": fund_out
            }


'''
function: take tick data into database
@:param start_data  date start at,format"2017-01-09",string
@:param end_data    data end at,format"2017-01-09",string
@:param code        stk code
@:return            write data to database,the same time,return the finale result
注意，有可能出现某一天数据下载失败的情况，而以后却无法对这一天的数据进行补充，
因为无法去判断是有数据下载失败，还是这一天本来就没有数据
'''


def write_dd_data_to_database(conn_param, start_date, end_date, code, big_than):
    table_name_in_db = "dd" + code

    date_range = pd.date_range(start=start_date, end=end_date)
    tick_data = date_range.map(lambda x: get_single_day_dd_data(date_param='%s' %x,
                                                                  code=code,
                                                                  big_than=big_than))
    # filter empty, result format:list(dict)
    tick_data_filter = list(filter(lambda x: not not x, list(tick_data)))

    finale_data_df = DataFrame(tick_data_filter)
    if not finale_data_df.empty:
        finale_data_df.to_sql(con=engine_dd, name=table_name_in_db, if_exists='append', index=False)

    ''' ------------------------------------main-------------------------------------------- '''


# 读取total stk 信息
total_stk_info_mysql = get_total_table_data(conn_basic, total_stk_info_table_name)

# 遍历stk，数据进行更新
for index in total_stk_info_mysql.index:
    stk_code = total_stk_info_mysql.loc[index, 'code']
    timeToMarket = total_stk_info_mysql.loc[index, 'timeToMarket']

    # 查看表内是否有相应stk信息，如果有，找出其最近日期，从最近日期开始读取
    if is_table_exist(conn=conn_tick, database_name=stk_tick_data_db_name, table_name='dd'+stk_code):

        # 获取表内的最近的日期，并按降序排序，即第一个是时间范畴上最晚的
        date_in_table_latest = pd.read_sql(con=conn_dd, sql='SELECT date FROM ' + 'dd' + stk_code)\
                                    .sort_values(by='date', ascending=False).loc[0, 'date']

        # 判断表内最新的时间是否小于当前时间
        if (convert_str_to_date(date_in_table_latest) - get_current_date()).days < 0:
            write_dd_data_to_database(conn_dd, start_date=date_in_table_latest,
                                        end_date=get_current_date_str(), code=stk_code, big_than=400)

            # 打印信息
            print('stk:' + stk_code + ' table exist,update it from ' + date_in_table_latest + ' to ' +get_current_date_str() + '\n')

    else:
        # 从头下载所有数据
        write_dd_data_to_database(conn_dd, start_date=date_str_std(timeToMarket),
                                    end_date=get_current_date_str(), code=stk_code, big_than=400)

        # 打印信息
        print('stk:' + stk_code + ' table does not exist,update it totally!\n')

