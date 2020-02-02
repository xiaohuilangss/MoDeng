# encoding=utf-8

"""

创建一个关于海选的类，用来处理灯神中输入的关于海选的命令，主要有：

1、创建筛选规则

    b、选择规则种类
        macd、rsi、sar、close_rank、age、today_cp
    c、编辑规则
    d、
2、删除筛选规则：


2、查看筛选规则

3、配置pdf存放路径

4、定时启动

"""
import os
import json

import time
import wx
import tkinter as tk
from tkinter import filedialog

class SelectCmd:
    def __init__(self):
        self.json_file = 'select.json'
        self.json_dir = 'C:\MoDeng\data/'
        self.init_dict = {
                    'save_dir': '',
                    'filter_rule': []
                }
        self.config = {}

        self.pdf_save_dir = ''

        # 加载json文件
        self.load_json_file()

        self.help_str = \
        """
        海选相关命令：
        
        “增加规则 macd反转 日线”
        （释义：找出日线macd反转的股票）
        
        “增加规则 sar反转 半小时线” 
        （释义：筛选出半小时线sar反转的股票）
        
        “增加规则 close_rank 日线 300 0 14” 
        （释义：计算当天收盘价在近300天内的排名，找出排名处于0~14%之间的股票）
        
        “增加规则 rsi 半小时线 12 20 35”
        （释义：计算半小时线的rsi12指数，筛选出值处于20~35之间的标的）
        
        “增加规则 上市年龄 2 15”
        （释义：筛选出上市年龄处于2年~15年的标的）
        
        “增加规则 当日涨跌幅 5 10”
        （释义：筛选出当天涨跌幅在5%到10%之间的标的）
        
        “清空规则”
        （释义：清空所有海选过滤规则）
        
        “查看规则”
        （释义： 查看当前使用的规则）
        
        “删除规则 4”
        （释义：删除编号为4的规则，编号可以通过“查看规则”命令来查看）
        
        “帮助-海选规则”
        （释义：查看海选相关的命令）
        
        “规则-设置报告存放路径”
        （释义：设置最后生成的海选报告的存放路径）
        
        “执行海选”
        （释义：启动海选功能）
        """

    def load_json_file(self):
        """
        加载海选的json文件
        :return:
        """
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)

        if not os.path.exists(self.json_dir + self.json_file):
            with open(self.json_dir + self.json_file, 'w') as f:
                json.dump(self.init_dict, f)
                self.config = self.init_dict
        else:
            with open(self.json_dir + self.json_file, 'r') as f:
                self.config = json.load(f)

    def save_json_file(self):

        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)

        with open(self.json_dir + self.json_file, 'w') as f:
            json.dump(self.config, f)

    @staticmethod
    def input_str_filter(input_str):
        """
        根据空格进行过滤分割
        :param input_str:
        :return:
        """
        if ' ' in input_str:
            r = input_str.split(' ')
            return [x.replace(' ', '') for x in r]
        else:
            return [input_str]

    def add_rule_macd(self, input_str_):
        """
        增加macd反转规则
        增加规则 macd反转 半小时线
        :return:
        """

        error_note = \
            """
            -------------------------------------------------
            输入内容：%s
            格式错误！增加macd反转过滤规则的格式为：
            
            增加规则 macd反转 k线周期（半小时线、日线、周线）
            
            范例：
            “增加规则 macd反转 半小时线”
            --------------------------------------------------
            """ % self.input_str_format(str(input_str_))

        if (len(input_str_) != 3) | (not isinstance(input_str_, list)):
            return error_note

        if input_str_[1] != 'macd反转':
            return error_note

        self.config['filter_rule'].append({
            'describe': '筛选出"%s macd反转"的标的' % input_str_[2],
            'kind': 'macd反转',
            'data': {
                'k_kind': input_str_[2]
            },
            'priority': 2
        })
        self.save_json_file()
        return '成功增加%smacd反转过滤规则！' % input_str_[2]

    def add_rule_rsi(self, input_str_):
        """
        增加macd反转规则
        增加规则 macd反转 半小时线
        :return:
        """

        error_note = \
            """
            -------------------------------------------------
            格式错误！当前输入为：%s
            增加 rsi 过滤规则的格式为：
    
            增加规则 rsi rsi周期（5, 12, 30） rsi起始 rsi终止
    
            范例：
            “增加规则 rsi 日线 12 12 40”
            表示 计算“日线”的rsi12 指标，找出rsi12的值大于12小于40的标的
            --------------------------------------------------
            """ % self.input_str_format(str(input_str_))

        if (len(input_str_) != 6) | (not isinstance(input_str_, list)):
            return error_note
        if input_str_[1] != 'rsi':
            return error_note

        self.config['filter_rule'].append({
            'describe': '筛选出"%s的rsi%s的值处于%s到%s的范围内"的标的' % (input_str_[2], input_str_[3], input_str_[4], input_str_[5]),
            'kind': 'rsi',
            'data': {
                'k_kind': input_str_[2],
                'rsi_p': input_str_[3],
                'rsi_low': input_str_[4],
                'rsi_high': input_str_[5]
            },
            'priority': 2
        })

        success_note = \
        """
        增加rsi过滤规则成功！
        此条过滤规则将筛选出%srsi%s处于%s到%s范围内的标的!
        """ % (input_str_[2], input_str_[3], input_str_[4], input_str_[5])
        self.save_json_file()
        return success_note

    def add_rule_sar(self, input_str_):
        """
        增加sar反转规则
        增加规则 macd反转 半小时线
        :return:
        """

        error_note = \
            """
            -------------------------------------------------
            实际输入：%s
            格式错误！增加 sar 过滤规则的格式为：

            增加规则 sar k线周期

            范例：
            “增加规则 sar反转 日线”
            表示筛选出“日线”sar反转的标的
            --------------------------------------------------
            """ % self.input_str_format(str(input_str_))

        if (len(input_str_) != 3) | (not isinstance(input_str_, list)):
            return error_note
        if input_str_[1] != 'sar反转':
            return error_note

        self.config['filter_rule'].append({
            'describe': '筛选出"%s sar反转"的标的' % input_str_[2],
            'kind': 'sar反转',
            'data': {
                'k_kind': input_str_[2]
            },
            'priority': 2
        })

        success_note = '成功增加%ssar反转的筛选规则！' % input_str_[2]
        self.save_json_file()
        return success_note

    def add_rule_age(self, input_str_):
        """
        根据上市时间来筛选标的
        :return:
        """

        error_note = \
            """
            -------------------------------------------------
            格式错误！当前输入为：%s
            上市时间 过滤规则的格式为：

            增加规则 上市年龄 起始值 终止值

            范例：
            “增加规则 上市年龄 5 30”
            表示筛选上市年龄在5~30年的标的

            --------------------------------------------------
            """ % self.input_str_format(str(input_str_))

        if (len(input_str_) != 4) | (not isinstance(input_str_, list)):
            return error_note

        if input_str_[1] != '上市年龄':
            return error_note

        self.config['filter_rule'].append({
            'describe': '筛选出"上市年龄处于%s年到%s年之间"的标的' % (input_str_[2], input_str_[3]),
            'kind': '上市年龄',
            'data': {
                'age_low': input_str_[2],
                'age_high': input_str_[3]
            },
            'priority': 0
        })

        success_note = \
            """
            成功增加上市年龄的筛选规则！
            """
        self.save_json_file()
        return success_note

    def add_rule_cp(self, input_str_):
        """
        根据最后一个交易日的收盘涨跌幅进行筛选
        :param input_str_:
        :return:
        """

        error_note = \
            """
            -------------------------------------------------
            格式错误！当前输入为：%s
            上市时间 过滤规则的格式为：

            增加规则 当日涨跌幅 起始值 终止值

            范例：
            “增加规则 当日涨跌幅 -1 8”
            表示筛选当日涨跌幅在-0.01~0.08到的标的
            --------------------------------------------------
            """ % self.input_str_format(str(input_str_))

        if (len(input_str_) != 4) | (not isinstance(input_str_, list)):
            return error_note

        if input_str_[1] != '当日涨跌幅':
            return error_note

        self.config['filter_rule'].append({
            'describe': '筛选出"当日涨跌幅处于百分之%s到百分之%s之间"的标的' % (input_str_[2], input_str_[3]),
            'kind': '当日涨跌幅',
            'data': {
                'cp_low': input_str_[2],
                'cp_high': input_str_[3]
            },
            'priority': 0
        })

        self.save_json_file()

        return '成功增加当日涨跌幅筛选规则！'

    def add_rule_close_rank(self, input_str_):
        """
        根据收盘价历史排名过滤
        :param input_str_:
        :return:
        """

        error_note = \
            """
           -------------------------------------------------
           格式错误！当前输入为：%s
           价格排名 过滤规则的格式为：

           增加规则 close_rank k线周期 数量 排名起始 排名终止

           范例：
           “增加规则 close_rank 日线 300 0 20”
           表示筛选当前价格在300天的价格排名在0~20之间的标的

           排名权值范围为0~100， 0为300天内最低价，100意味着300天内最高价
           --------------------------------------------------
           """% self.input_str_format(str(input_str_))

        if (len(input_str_) != 6) | (not isinstance(input_str_, list)):
            return error_note
        if input_str_[1] != 'close_rank':
            return error_note

        self.config['filter_rule'].append({
            'describe': '"计算当前%s收盘价在近%s单位时间收盘价中的排名，筛选出排名处于%s到%s之间"的标的！' % (input_str_[2], input_str_[3], input_str_[4], input_str_[5]),
            'kind': 'close_rank',
            'data': {
                'k_kind': input_str_[2],
                'amount': input_str_[3],
                'rank_low': input_str_[4],
                'rank_high': input_str_[5]
            },
            'priority': 1
        })

        success_note = \
            """
            成功增加%s收盘价排名的筛选规则！
            """ % input_str_[2]
        self.save_json_file()

        return success_note

    def rule_input_pro(self, input_str):
        """
        增加规则
        :return:
        """
        ipt_ = self.input_str_filter(input_str)

        if ipt_[0] == '增加规则':

            if ipt_[1] == 'sar反转':
                r = self.add_rule_sar(ipt_)

            elif ipt_[1] == 'rsi':
                r = self.add_rule_rsi(ipt_)

            elif ipt_[1] == 'close_rank':
                r = self.add_rule_close_rank(ipt_)

            elif ipt_[1] == '上市年龄':
                r = self.add_rule_age(ipt_)

            elif ipt_[1] == 'macd反转':
                r = self.add_rule_macd(ipt_)

            elif ipt_[1] == '当日涨跌幅':
                r = self.add_rule_cp(ipt_)

            else:
                r = '不识别的规则类型！'

        elif ipt_[0] == '删除规则':
            r = self.delete_rule(ipt_)

        elif ipt_[0] == '查看规则':
            r = self.inspect_rule()

        elif ipt_[0] == '清空规则':
            r = self.clear_rule()

        elif ipt_[0] == '帮助-海选规则':
            r = self.help_str

        elif ipt_[0] == '规则-设置报告存放路径':
            try:
                r = '路径设置成功！存放路径为：\n' + self.select_pdf_save_dir() + '\n'
            except Exception as e_:
                r = '\n设置报告存放路径出错！原因：\n%s\n请重试\n' % str(e_)

        else:
            r = '不识别的规则类型！'

        # if '成功' in r:
        #     self.save_json_file()

        return r

    def clear_rule(self):
        self.config['filter_rule'] = []
        self.save_json_file()
        return '成功清空过滤规则！'

    @staticmethod
    def rule_str_format(rule_dict):
        """
        将字典格式的原生rule翻译成字符串格式的白话文
        :param rule_dict:
        :param rule_json:
        :return:
        """
        rule_dict['kind'] = rule_dict['kind']

    def inspect_rule(self):

        if len(self.config['filter_rule']) == 0:
            return '当前无海选过滤规则！'

        num = 0
        str_ = ''
        for rule in self.config['filter_rule']:
            str_ = str_ + str(num) + '\t' + rule['describe'] + '\n'
            num = num + 1

        return str_

    @staticmethod
    def input_str_format(input_str):
        """
        对字符串格式的输入命令进行格式化
        :return:
        """
        return input_str.replace('[', '"').replace(']', '"').replace("'", '').replace(',', ' ')

    def delete_rule(self, input_):

        delete_error = \
        """
        格式错误！当前输入格式为：%s

        删除规则命令的格式为（引号内为输入内容）：

        “删除规则 2”（删除第二条规则之意）

        """ % self.input_str_format(str(input_)) + '\n当前规则有：\n' + self.inspect_rule()

        if len(self.config['filter_rule']) == 0:
            return '当前无规则可删！'

        if len(input_) != 2:
            return delete_error
        try:
            rule_pop = self.config['filter_rule'].pop(int(input_[1]))
            self.save_json_file()
            str_return = '成功删除规则：\n %s' % str(rule_pop) + '\n\n剩余规则有：\n' + self.inspect_rule()
            return str_return

        except Exception as e_:
            str_ = \
            """
            删除规则失败，原因：
            %s
            """ % str(e_) + delete_error
            return str_

    def select_pdf_save_dir(self):
        """
        设置生成的pdf报告存放的文件夹
        :return:
        """

        rt = tk.Tk()
        _ = rt.withdraw()
        dir_ = filedialog.askdirectory()
        rt.destroy()
        self.save_json_file()
        return dir_


if __name__ == '__main__':

    select = SelectCmd()

    print(select.rule_input_pro('增加规则 macd反转 日线 4'))
    end = 0
