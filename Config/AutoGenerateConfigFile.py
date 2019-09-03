# encoding = utf-8

"""
对配置文件进行检测
"""
import os
import json

config_path = 'c:/MoDeng/'
data_source_url = config_path+'data_source.json'
stk_config_url = config_path+'stk_config.json'


def checkConfigFile():

    # 配置文件未准备好 标志位
    configReadyFlag = True

    # 如果没有该文件夹，创建！
    if not os.path.exists(config_path):
        os.makedirs(config_path)
        configReadyFlag = False

    # 依次检查是否有相应的配置文件，如果没有，创建！
    if not os.path.exists(data_source_url):
        with open(data_source_url, 'w') as f:
            json_dict = {
                'JQ_Id': '',
                'JQ_passwd': ''
            }
            json.dump(json_dict, f)
            configReadyFlag = False

    if not os.path.exists(stk_config_url):
        with open(stk_config_url, 'w') as f:
            json_dict = {
                          "pcr": 1.8,
                          "concerned_stk": ["000333", "300059"],
                          "buy_stk": ["600256", "603421",  "300243", "300263"],
                          "safe_stk": ["000333",  "002456", "000725", "300508"]
    }
            json.dump(json_dict, f)
            configReadyFlag = False

    if not configReadyFlag:
        print(
            '\n\n' +
            '检测到您有配置文件不存在，可能是您第一次使用软件。系统已经为您创建了初始的配置文件，请完善相关参数的配置！' + '\n\n' +
            '配置文件路径为：' + config_path + '\n\n' +
            '需要完善的相关参数为：' + '\n' +
            '1、在data_source.json文件中填写聚宽数据的账号和密码，字符串格式。没有聚宽数据的账号可以在此免费网址注册：\n' +
            'https://www.joinquant.com/user/login/index?type=register\n'+
            '2、在stk_config.json文件中的 buy_stk 字段中填写当前您持仓的股票代码，软件会在交易时间段定时分析相关股票。\n'+
            '3、在stk_config.json文件中的 concerned_stk 字段中填写当前您未购买但是感兴趣的股票，没有可不填。\n' +
            '请完善配置文件后重试！'
        )

        exit(1)


if __name__ == '__main__':

    checkConfigFile()