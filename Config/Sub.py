# encoding = utf-8
from Config.AutoGenerateConfigFile import stk_config_url
import json


def readConfig():
    with open(stk_config_url, 'r') as f:
        return json.load(f)


if __name__ == '__main__':

    r = readConfig()
    end = 0
