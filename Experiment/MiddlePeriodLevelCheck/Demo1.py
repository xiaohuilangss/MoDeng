# encoding=utf-8

"""

将关心的和持仓的股票的中等长度的小时数据保存到json文件中
"""
from Config.AutoGenerateConfigFile import config_path, data_dir
from Config.Sub import readConfig


# 获取股票列表
from Experiment.RelativeRank.Sub import get_k_data_JQ
from SDK.MyTimeOPT import get_current_date_str, add_date_str


def update_middle_period_hour_data():
    stk_list = readConfig()['buy_stk'] + readConfig()['concerned_stk']
    # stk_list = readConfig()['buy_stk']

    # 获取股票的小时数据
    result = []
    for stk in stk_list:
        df_hour = get_k_data_JQ(stk, count=None, start_date=add_date_str(get_current_date_str(), -60), freq='60m')
        result.append({
            stk: list(df_hour['close'].values)
        })

    with open(data_dir+'middlePeriodHourData.json', 'w') as f:
        json.dump(result, f)


if __name__ == '__main__':

    from DataSource.auth_info import *
    update_middle_period_hour_data()
    end = 0

