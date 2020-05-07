# coding=utf-8


from sdk.SDKHeader import *



def update_single_stk_k_data(conn_param, k_database_name, stk_code_param):
    """
    更新单只stk的K数据

    :param conn_param:
    :param k_database_name:
    :param stk_code_param:
    :return:
    """

    stk_code_str = str(stk_code_param)

    # first we should judge if the table exist in database
    if not is_table_exist(conn=conn_param, table_name='k' + stk_code_str, database_name=k_database_name):

        print('stock ' + stk_code_str + ' does not exist in database!\n')
        try:
            data_single_stk = ts.get_k_data(stk_code_str,start='2001-01-01')
            if not data_single_stk.empty:
                data_single_stk.to_sql(con=engine_k, name='k' + stk_code_str, if_exists='append', index=False)
            else:
                print('stock ' + stk_code_str + ' 从网上下载下来的数据是空的!\n')
        except:
            print('函数update_single_stk_k_data：下载新的数据并写入数据库时出错！')
    else:

        data_db = get_total_table_data(conn_param, 'k' + stk_code_str)
        latest_date_local = data_db.sort_values(by='date', ascending=False).reset_index().loc[0,'date']
        date_in_local = convert_str_to_date(str(latest_date_local))

        # 如果数据库中数据的最晚时间与当前时间不一样，则进行更新！“数据库最晚日期加一天”~“当前日期”
        if (date_in_local - get_current_date()).days != 0:
            ts.get_k_data(stk_code_str, start=convert_date_to_str(date_in_local + datetime.timedelta(days=1)))\
                .to_sql(con=engine_k, name='k' + stk_code_str, if_exists='append', schema=k_database_name, index=False)
            print('stock ' + stk_code_str + ' exist in database!\n' + 'last update date is ' + str(latest_date_local)\
                  + ',we update it to now successful!\n\n')
        else:
            print('stock ' + stk_code_str + ' exist in database!\n' + 'last update date is ' + str(latest_date_local) \
                  + ',we did not need to update it!\n\n')


def update_K_data():
    """
    按照stk代码列表更新所有stk的K数据

    :return:
    """
    total_stk_info_mysql = get_total_table_data(conn_basic, total_stk_info_table_name)

    for index in total_stk_info_mysql.index:
        stk_code = total_stk_info_mysql.loc[index, 'code']
        update_single_stk_k_data(conn_param=conn_k, k_database_name=stk_k_data_db_name, stk_code_param=stk_code)

    # 更新各大指数数据（上证、深证、创业板、中小板）
    update_index_K_data()


def update_index_K_data():
    """
    更新各大指数数据（上证、深证、创业板、中小板）

    :return:
    """


    for b_ele in ['sh','sz','zxb','cyb']:
        update_single_stk_k_data(conn_param=conn_k, k_database_name=stk_k_data_db_name, stk_code_param=b_ele)


# ---------------------------- 测试代码 -------------------------------------------------
# update_K_data()



