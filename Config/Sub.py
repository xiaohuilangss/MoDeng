# encoding = utf-8
from Config.AutoGenerateConfigFile import stk_config_url
import json


def readConfig():
    with open(stk_config_url, 'r') as f:
        return json.load(f)


dict_stk_list = {
    'Index': readConfig()['index_stk'],
    'Buy': readConfig()['buy_stk'],
    'Concerned': readConfig()['concerned_stk']
}

if __name__ == '__main__':

    r = readConfig()
    end = 0
