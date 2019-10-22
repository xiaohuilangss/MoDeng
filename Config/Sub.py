# encoding = utf-8
from Config.AutoGenerateConfigFile import stk_config_url
import json
import threading

# 配置文件写入锁
config_lock = threading.Lock()


def readConfig():
    with open(stk_config_url, 'r') as f:
        return json.load(f)


def writeConfig(key, value):
    """
    向配置文件中写入信息
    :param key:
    :param value:
    :return:
    """
    if config_lock.acquire():
        try:
            json_config = readConfig()
            json_config[key] = value

            with open(stk_config_url, 'w') as f:
                json.dump(json_config, f)

        except Exception as e:
            print('函数 writeConfig：写入配置文件出错，原因：\n' + str(e))

        finally:

            # 释放锁
            config_lock.release()






dict_stk_list = {
    'Index': list(enumerate(list(set(readConfig()['index_stk'])))),
    'Buy': list(enumerate(list(set(readConfig()['buy_stk'])))),
    'Concerned': list((enumerate(list(set(readConfig()['concerned_stk']).difference(set(readConfig()['buy_stk']))))))
}

if __name__ == '__main__':

    r = readConfig()
    end = 0
