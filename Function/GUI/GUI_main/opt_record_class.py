# encoding=utf-8
import json
import os

import math
import pandas as pd

from Global_Value.file_dir import json_file_url
from Global_Value.thread_lock import opt_record_lock
from sdk.MyTimeOPT import get_current_datetime_str
import numpy as np


class OptRecord:
    def __init__(self, opt_record_file_url_, stk_code):

        # 用来初始化的格式
        self.opt_dict_init = {
            'b_opt': [],
            'p_last': None,
            'has_flashed_flag': True,
            'total_earn': 0,
            'last_prompt_point': -1
        }

        self.opt_record_file_url = opt_record_file_url_
        self.stk_code = stk_code

        # 在初始化中读取文件
        self.opt_record = self.read_json()
        self.opt_record_stk = self.get_stk()

    def get_stk(self):

        if pd.isnull(self.opt_record):
            return {}
        else:
            if self.stk_code in self.opt_record.keys():
                return self.opt_record[self.stk_code]
            else:
                return {}

    def is_stk_in_config(self):
        """
        判断stk是否在配置文件中
        :return:
        """
        return self.stk_code in self.opt_record.keys()

    def add_b_opt(self, price, amount):
        """
        记录买入操作
        :return:
        """
        b_opt = self.get_config_value('b_opt')

        if pd.isnull(b_opt):
            b_opt = [dict(time=get_current_datetime_str(), p=price, amount=amount)]
        else:
            b_opt = b_opt.append(dict(time=get_current_datetime_str(), p=price, amount=amount))

        self.set_config_value('b_opt', b_opt)

    def read_json(self):
        """
        读取json文件
        要不要加try catch？
        :return:
        """
        # 已有文件，打开读取
        if os.path.exists(self.opt_record_file_url):
            if opt_record_lock.acquire():
                try:
                    with open(self.opt_record_file_url, 'r') as f:
                        return json.load(f)
                except Exception as _e:
                    print('函数OptRecord.read_json:出错！ \n' + str(_e))
                finally:
                    opt_record_lock.release()
        else:
            return {}

    def get_config_value(self, key_):
        """
        获取指定股票指定字段的值，没有返回None
        :param stk:
        :param key_:
        :return:
        """
        if self.stk_code in self.opt_record.keys():
            opt_r_stk = self.opt_record[self.stk_code]
            if key_ in opt_r_stk.keys():
                return opt_r_stk[key_]
            else:
                return None
        else:
            # 如果没有这支股票的信息，则进行初始化，并保存到文件中
            self.opt_record[self.stk_code] = self.opt_dict_init
            self.save_json()
            return None

    def set_config_value(self, key_, value):
        """
        设定某个字段的值
        :param value:
        :param key_:
        :return:
        """
        if self.stk_code in self.opt_record.keys():
            opt_r_stk = self.opt_record[self.stk_code]
            opt_r_stk[key_] = value
            self.save_json()
        else:
            # 如果没有这支股票的信息，则进行初始化，并保存到文件中
            self.opt_record[self.stk_code] = self.opt_dict_init
            self.opt_record[self.stk_code][key_] = value
            self.save_json()

    def save_json(self):
        """
        保存json文件
        :return:
        """
        if opt_record_lock.acquire():
            try:
                with open(self.opt_record_file_url, 'w') as f:
                    json.dump(self.opt_record, f)
            except Exception as e:
                print('函数OptRecord.save_json:出错！ \n' + str(e))
            finally:
                opt_record_lock.release()
