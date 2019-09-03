# encoding = utf-8
from Config.AutoStkConfig import rootPath

import json

# 配置文件的路径
config_file_path = rootPath + '/Config/config.json'


def readConfig():
    with open(config_file_path, 'r') as f:
        return json.load(f)


if __name__ == '__main__':

    r = readConfig()
    end = 0
