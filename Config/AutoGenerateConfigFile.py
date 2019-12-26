# encoding = utf-8

"""
对配置文件进行检测
"""
import os
import json

from Global_Value.file_dir import config_path, data_source_url, data_dir, stk_config_url


def checkConfigFile():

    # 配置文件未准备好 标志位
    configReadyFlag = True

    # 如果没有该文件夹，创建！
    if not os.path.exists(config_path):
        os.makedirs(config_path)
        configReadyFlag = False

    # 如果没有data文件夹，创建它
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 依次检查是否有相应的配置文件，如果没有，创建！
    if not os.path.exists(data_source_url):
        with open(data_source_url, 'w') as f:
            json_dict = {
                'JQ_Id': '',
                'JQ_passwd': '',
                'TS_token': ''
            }
            json.dump(json_dict, f)
            configReadyFlag = False

    if not os.path.exists(stk_config_url):
        with open(stk_config_url, 'w') as f:
            json_dict = {
                          "pcr": 1.8,
                          "index_stk": ["sh", "sz", "cyb"],
                          "concerned_stk": ["000333", "300059"],
                          "buy_stk": ["600256", "603421",  "300243", "300263"],
                          "safe_stk": ["000333",  "002456", "000725", "300508"]
    }
            json.dump(json_dict, f)
            configReadyFlag = False

    if not configReadyFlag:
        print(
            """
            检测到您有配置文件不存在，可能是您第一次使用软件。系统已经为您创建了初始的配置文件，请完善相关参数的配置！
            
            配置文件路径为：C:/MoDeng/
            
            需要完善的相关参数为：
            1、在data_source.json文件中的“JQ_Id”和“JQ_passwd”填写聚宽数据的账号和密码，字符串格式。
            
            没有聚宽数据的账号可以在此免费网址注册：
            https://www.joinquant.com/default/index/sdk?channelId=04010d057cf9ef27d61aeeed694acab9
            
            2、在data_source.json文件中“TS_token”填写tushare数据的token，字符串格式。
            
            没有聚宽数据的账号可以在此免费网址注册：
            https://tushare.pro/register?reg=125290
            
            3、在stk_config.json文件中的 buy_stk 字段中填写当前您持仓的stk代码，软件会在交易时间段定时分析相关stk。
            4、在stk_config.json文件中的 concerned_stk 字段中填写当前您未购买但是感兴趣的stk，没有可不填。
            
            请完善配置文件后重试！
            
            """

        )

        input('请按照提示进行配置，完成后重启即可！')


if __name__ == '__main__':

    checkConfigFile()