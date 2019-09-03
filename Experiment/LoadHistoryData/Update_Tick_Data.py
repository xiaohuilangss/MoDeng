# encoding = utf-8
from random import randint

from SDK.SDKHeader import *

from Config.GlobalSetting import *
from SDK.DBOpt import *

'''
function:get tick data in single day,and then write it to database,
            table field contain:
            date,price_start,
            price_end,
            total_in,
            total_out,
            big_in,
            big_out,
            medium_in,
            medium_out,
            small_in,
            small_out
@:param date
@:param code stk code,str format
@:param small_than: volume small than this value means it's a small bill
@:param big_than:   volume big than this value means it's a big bill
@:param src : 数据源选择，可输入sn(新浪)、tt(腾讯)、nt(网易)，默认sn
        retry_count : int, 默认 3
                  如遇网络等问题重复执行的次数
        pause : int, 默认 0
                 重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
@:return take the result write into database table,name with tick_code
'''
def get_single_day_tick_data(date_param, code, small_than, big_than, retry_count_param=6, pause_param=1):

    # 反复尝试数据下载
    success_flag = False
    while not success_flag:

        global src_current
        try:
            native_data_today_df = ts.get_tick_data(code=code, date=date_param, retry_count=retry_count_param, pause=pause_param, src=src_current)
            success_flag = True
        except:
            print('源:' + src_current + ' 下载数据失败，延时尝试！')
            src_current = ('tt', 'sn', 'nt')[randint(0, 2)]     # 更换数据来源
            time.sleep(gSleepTime)

    print('代码：' + code + ' 日期：' + date_param + ' 数据下载成功！')

    # if data is empty,it would be error,when sorted by time!,so a judgement here is necessary!
    if native_data_today_df is None:
        data_today_sort_by_time = native_data_today_df
    else:
        data_today_sort_by_time = native_data_today_df.sort_values(by=["time"])

    try:
        # if there is no today's data,return a empty dictionary
        if data_today_sort_by_time is None:
            print('代码：'+code+' 日期：' + date_param + ' 没有当天数据！')
            return {}

        # 如果没有当天的数据，返回!
        if (len(native_data_today_df) <= 3) & math.isnan(native_data_today_df.loc[0, "price"]):
            print('代码：' + code + ' 日期：' + date_param + ' 没有当天数据！')
            return {}

        # 如果没有当天的数据，返回!
        if native_data_today_df.empty:
            print('代码：' + code + ' 日期：' + date_param + ' 没有当天数据！')
            return {}
    except:
        print("遭遇未知数据类型！")
        return {}

    price_start = data_today_sort_by_time.head(1).price.sum()
    price_end = data_today_sort_by_time.tail(1).price.sum()
    try:
        total_in = data_today_sort_by_time[data_today_sort_by_time.type == "买盘"].amount.sum()
        total_out = data_today_sort_by_time[data_today_sort_by_time.type == "卖盘"].amount.sum()
    except:
        print("unexpected error!")

    big = data_today_sort_by_time[data_today_sort_by_time.volume > big_than]
    big_in = big[big.type == "买盘"].amount.sum()
    big_out = big[big.type == "卖盘"].amount.sum()

    medium = data_today_sort_by_time[(data_today_sort_by_time.volume < big_than) & (data_today_sort_by_time.volume > small_than)]
    medium_in = medium[medium.type == "买盘"].amount.sum()
    medium_out = medium[medium.type == "卖盘"].amount.sum()

    small = data_today_sort_by_time[data_today_sort_by_time.volume < small_than]
    small_in = small[small.type == "买盘"].amount.sum()
    small_out = small[small.type == "卖盘"].amount.sum()

    return {"date": date_param,
            "price_start": price_start,
            "price_end": price_end,
            "total_in": total_in,
            "total_out": total_out,
            "big_in": big_in,
            "big_out": big_out,
            "medium_in": medium_in,
            "medium_out": medium_out,
            "small_in": small_in,
            "small_out": small_out}

'''
function: take tick data into database
@:param start_data  date start at,format"2017-01-09",string
@:param end_data    data end at,format"2017-01-09",string
@:param code        stk code
@:return            write data to database,the same time,return the finale result
'''
def write_tick_data_to_database(conn_param, start_date, end_date, code, big_than, small_than):

    # 如果其出道较早，可能没有当时的数据，所以需要判断有数据记载的最早时间，使用“月跳”的方式，本月此日如果没有数据，就下载下月此日的数据，一旦下载到，
    # 就将其定义为起始时间
    # 具体方法：
    # 构建以当前日期为起点，长度为4天的一个时间段，若这4天里一天数据都没有，则说明当月没有数据，直接跨到下个月
    start_date_temp = start_date

    while minus_date_str(start_date_temp,get_current_date_str()) < 0:

        # 构造3天的日期序列
        end_date_temp = add_date_str(start_date_temp, 4)

        # 如果日期很近，则不用这种规则，直接跳出while循环
        if minus_date_str(end_date_temp,get_current_date_str()) > 0:
            break

        date_range_temp = pd.date_range(start=start_date_temp, end=end_date_temp).sort_values(ascending=False)

        # 下载这3天的数据
        tick_data_temp = date_range_temp.map(lambda x: str(x)[:10]).map(lambda x: get_single_day_tick_data(date_param=x,
                                                                  code=code,
                                                                  small_than=small_than,
                                                                  big_than=big_than))



        if len(DataFrame(list(filter(lambda x: not not x, list(tick_data_temp))))) < 2:

            # 起始时间往后延迟100天
            start_date_temp = add_date_str(start_date_temp,days=101)

            print("本月可能没有数据，将日期跳到下个月！")
        else:

            # 将结束时间在起始时间的基础上延后设定时间，以形成本次的下载档期
            end_date_temp = add_date_str(start_date_temp, 100)

            # 如果结束时间超过了当前时间，则以当前时间为结束时间
            if minus_date_str(end_date_temp, get_current_date_str()) > 0:
                end_date_temp = get_current_date_str()

            # 下载该时间段的数据
            date_range = pd.date_range(start=start_date_temp, end=end_date_temp)
            tick_data = date_range.map(lambda x: str(x)[:10]).map(lambda x: get_single_day_tick_data(date_param=x,
                                                                                                     code=code,
                                                                                                     small_than=small_than,
                                                                                                     big_than=big_than))
            # filter empty, result format:list(dict)
            tick_data_filter = list(filter(lambda x: not not x, list(tick_data)))

            finale_data_df = DataFrame(tick_data_filter)
            if not finale_data_df.empty:
                finale_data_df.to_sql(con=engine_tick, name='tick'+code, if_exists='append', index=False)

            # 将结束时间+1 赋值给起始时间
            start_date_temp = add_date_str(end_date_temp,days=1)


'''
在表已经存在的情况下更新表
'''
def update_table_exist(connParam,latest_date_in_table,codeParam,small_than_Param,big_than_Paran):

    load_date_start = add_date_str(convert_date_to_str(latest_date_in_table),1)
    if minus_date_str(load_date_start,get_current_date_str())>=0:
        print('函数update_table_exist：表中的日期已经是最新的了！不需要更新！')
        return

    # 下载从表内最新的日期到当前这段时间的数据
    date_range = pd.date_range(start=load_date_start, end=get_current_date_str())
    tick_data = date_range.map(lambda x: str(x)[:10]).map(lambda x: get_single_day_tick_data(date_param=x,
                                                                                             code=codeParam,
                                                                                             small_than=small_than_Param,
                                                                                             big_than=big_than_Paran))
    # filter empty, result format:list(dict)
    tick_data_filter = list(filter(lambda x: not not x, list(tick_data)))

    finale_data_df = DataFrame(tick_data_filter)
    if not finale_data_df.empty:
        finale_data_df.to_sql(con=connParam, name='tick'+codeParam, if_exists='append', index=False)

''' ------------------------------------main-------------------------------------------- '''
# 遍历stk，对tick数据进行更新
for index in g_total_stk_info_mysql.index:
    stk_code = g_total_stk_info_mysql.loc[index, 'code']
    timeToMarket = g_total_stk_info_mysql.loc[index, 'timeToMarket']

    # 查看表内是否有相应stk信息，如果有，找出其最近日期，从最近日期开始读取
    if is_table_exist(conn=conn_tick, database_name=stk_tick_data_db_name, table_name='tick'+stk_code):

        # 获取表内的最近的日期，并按降序排序，即第一个是时间范畴上最晚的
        date_in_table_latest = convert_str_to_date(str(pd.read_sql(
            con=conn_tick, sql='SELECT date FROM ' + 'tick' + stk_code)
                                                       .sort_values(by='date', ascending=False)
                                                       .reset_index().loc[0, 'date']))

        # 判断表内最新的时间是否小于当前时间
        if (date_in_table_latest - get_current_date()).days < 0:
            update_table_exist(connParam=engine_tick,latest_date_in_table=date_in_table_latest,codeParam=stk_code,small_than_Param=50,big_than_Paran=400)
            # write_tick_data_to_database(conn_tick, start_date=convert_date_to_str(date_in_table_latest + datetime.timedelta(days=1)),
            #                             end_date=get_current_date_str(), code=stk_code, big_than=400, small_than=50)

            # 打印信息
            print('stk:' + stk_code + ' table exist,update it from ' + convert_date_to_str(date_in_table_latest) +
                  ' to ' + get_current_date_str() + '\n')

    else:
        # 从头下载所有数据
        # write_tick_data_to_database(conn_tick, start_date=date_str_std(timeToMarket),
        #                             end_date=get_current_date_str(), code=stk_code, big_than=400,
        #                             small_than=50)
        #
        # # 打印信息
        # print('stk:' + stk_code + ' table does not exist,update it totally!\n')

        # 获取当天日期
        travel_date = get_current_date_str()

        # stop explore 标志位 失败次数计数器
        # 当前机制为，从今天开始往前下载，遇到下载失败的情况，便将失败次数递增，若失败次数超过阈值，即停止下载，如果后来成功了，则失败次数置0
        stop_explore_flag = False
        fail_count = 0

        # 用于盛放数据的list
        result = []

        # 开始从当下往以前下载数据
        while not stop_explore_flag:

            # 下载该日期数据并存储
            single_day_tick_data = get_single_day_tick_data(date_param=travel_date,code=stk_code,big_than=400, small_than=50)
            result.append(single_day_tick_data)

            # 日期数据递减
            travel_date = add_date_str(travel_date,-1)

            # 计算失败次数
            if len(single_day_tick_data)==0:
                fail_count=fail_count+1
            else:
                fail_count=0
            print("连续失败次数："+str(fail_count))


            # 如果连续12天没有下载数据
            if fail_count > 15:
                stop_explore_flag = True

        # filter empty, result format:list(dict)
        tick_data_filter = list(filter(lambda x: not not x, result))

        finale_data_df = DataFrame(tick_data_filter)
        if not finale_data_df.empty:
            finale_data_df.sort_values(by="date").reset_index(drop=True).to_sql(con=engine_tick, name="tick" + stk_code, if_exists='append', index=False)
