# encoding = utf-8

from Config.GlobalSetting import *
'''
函数功能：搜索给定时间段内的close最低点，比如time_span_param = 20,即搜索20天内close最低点

@:parameter data_df_param   k数据，样例格式：

           date    open   close    high     low   volume    code
0    2015-02-04  26.814  26.434  27.078  26.322  22616.0  300508
1    2015-02-05  26.322  27.068  28.174  26.093  38915.0  300508
2    2015-02-06  26.800  26.176  27.297  25.859  18764.0  300508

@:parameter time_span_param     时间段，从当前往前推，单位为天

@:return float 格式 最低点值
'''


def compare_low_pot(kdata_df_param,time_span_param):

    try:
        target_date_str = add_date_str(get_current_date_str(),-1*time_span_param)
        target_df = kdata_df_param[(kdata_df_param.date>target_date_str)]
        low_pot = target_df[target_df.close == min(target_df.close)].reset_index(drop=True).iloc[0]
        now_pot = target_df.sort_values(by='date',ascending = False).head(1).reset_index(drop=True).iloc[0]
        return {
            "low_date": low_pot.date,
            "low_close": low_pot.close,
            "now_date": now_pot.date,
            "now_close": now_pot.close,
            "change_ratio": (now_pot.close - low_pot.close) / now_pot.close,
            "code":now_pot.code
        }
    except:
        return {}
'''
获取所有stk的low pot信息
'''
def get_total_low_pot_df():
    low_pot_list = []
    for singleStk in g_total_stk_code:
        if is_table_exist(conn_k, stk_k_data_db_name, 'k' + singleStk):
            low_pot_list.append(compare_low_pot(get_total_table_data(conn=conn_k, table_name='k' + singleStk), 365))
            DataFrame(low_pot_list).sort_values(by='change_ratio', ascending=False)
            print('完成' + singleStk)

    low_pot_df = DataFrame(low_pot_list).sort_values(by='change_ratio',ascending=True)
    return low_pot_df

#-------------------------正文---------------------------------------
low_pot_csv_file_path = g_debug_file_url+'lowPot'+get_current_date_str()+'.csv'


get_total_low_pot_df().to_csv(low_pot_csv_file_path)

# write_dict_list_to_csv(profit_list,low_pot_csv_file_path)
# profit_list_from_csv = read_csv_to_dict_list(low_pot_csv_file_path)
#
# DataFrame(profit_list_from_csv).sort_values(by='change_ratio',ascending=True).to_csv(low_pot_csv_file_path)
#
# end = 0


# result = compare_low_pot(get_total_table_data(conn=conn_k,table_name='k300508'),365)
# end = 0