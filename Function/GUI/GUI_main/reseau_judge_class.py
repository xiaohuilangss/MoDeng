# encoding=utf-8
import json
import os

from Config.Sub import read_config
from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_current_price_JQ
from Function.GUI.GUI_main.opt_record_class import OptRecord
from Global_Value.file_dir import opt_record, opt_record_file_url, json_file_url
from Global_Value.p_diff_ratio_last import RSV_Record
from Global_Value.thread_lock import opt_lock
from SDK.Debug_Sub import debug_print_txt

import pandas as pd
import numpy as np
import math

from SDK.MyTimeOPT import get_current_datetime_str
from SDK.StdForReseau.Sub import get_single_stk_reseau


class ReseauJudge:
    def __init__(self, stk_code, opt_record_, debug=False):
        self.opt_record = opt_record_
        self.stk_code = stk_code
        self.debug = debug
        self.str_gui = {
            'note': '',
            'msg': ''
        }
        self.add_msg('\n\n\n------------------------------------------\n' + code2name(stk_code) + ':开始进入本周期判断!\n')

        self.opt_record_stk = {}

        self.current_price = -1
        self.last_p = -1
        self.b_p_min = -1

        # self.money_each_opt = 5000
        # self.buy_amount = math.floor((self.money_each_opt / self.current_price) / 100) * 100

        self.thh_sale = 0
        self.thh_buy = 0

        self.has_flashed_flag = False
        self.pcr = 0

        self.opt_record_stk = opt_record_.opt_record_stk

    def get_current_price(self):
        """
        获取实时价格,返回True表示成功获取价格
        :return:
        """
        try:
            current_price = get_current_price_JQ(self.stk_code)

            str_ = '实时价格:' + str(current_price) + '\n'
            debug_print_txt('stk_judge', self.stk_code, str_, self.debug)
            self.add_msg(str_)

            if current_price == 0.0:
                self.add_msg(self.stk_code + 'price==0.0! 返回\n')
                return False
            else:
                self.current_price = current_price
                return True

        except Exception as e_:
            self.add_msg(self.stk_code + '获取实时price失败！\n' + str(e_) + '\n')
            return False

    def add_msg(self, str_):
        self.str_gui['msg'] = self.str_gui['msg'] + str_

    def add_note(self, str_):
        self.str_gui['note'] = self.str_gui['note'] + str_

    def get_opt_record_json(self):
        """
        判断该股票的opt_record配置是否正常
        :return:
        """

        # 如果没有相应的json文件，不进行判断，直接返回
        if pd.isnull(self.opt_record_stk) | (not bool(self.opt_record_stk)):
            str_ = code2name(self.stk_code) + '没有历史操作记录，不进行阈值判断！\n'
            debug_print_txt('stk_judge', self.stk_code, '函数 judge_single_stk：' + str_,
                            self.debug)
            self.add_msg(str_)
            return False

        elif len(self.opt_record_stk['b_opt']) == 0:
            str_ = code2name(self.stk_code) + '没有历史操作记录，不进行阈值判断！\n'
            debug_print_txt('stk_judge', self.stk_code, '函数 judge_single_stk：' + str_,
                            self.debug)
            self.add_msg(str_)
            return False
        else:
            return True

    @staticmethod
    def set_has_flashed_flag(json_file_url, stk_code, value=True):
        if os.path.exists(json_file_url):
            with open(json_file_url, 'r') as f:
                json_p = json.load(f)

            if stk_code in json_p.keys():
                json_p[stk_code]['has_flashed_flag'] = value
            else:
                json_p[stk_code] = {
                    'b_opt': [],
                    'p_last': None,
                    'has_flashed_flag': value,
                    'total_earn': 0
                }

            # 将数据写入
            with open(json_file_url, 'w') as f:
                json.dump(json_p, f)

            return 0
        else:
            return 2

    def did_have_flashed(self):
        """
        判断是否已经提示过
        :return:
        """
        # 如果没有该字段，加上
        if 'has_flashed_flag' not in self.opt_record_stk.keys():
            self.opt_record.set_config_value('has_flashed_flag', False)
            self.has_flashed_flag = False
        else:
            # 读取
            has_flashed_flag = self.opt_record_stk['has_flashed_flag']
            self.add_msg('已经进行过闪动提示?：' + {False: '是', True: '否'}.get(has_flashed_flag, '未知') + '\n')
    
            self.has_flashed_flag = has_flashed_flag

    def get_last_price(self):

        # 读取上次p和b操作中的最小p，备用
        self.last_p = self.opt_record_stk['p_last']
        self.b_p_min = np.min([x['p'] for x in self.opt_record_stk['b_opt']])

        str_ = '\n上次操作价格：' + str(self.last_p) + \
               '\n最小买入价格：' + str(self.b_p_min) + \
               '\n买入-波动率:' + '%0.3f' % (100.0 * (self.current_price - self.last_p) / self.last_p) + '%' + \
               '\n卖出-波动率:' + '%0.3f' % (100.0 * (self.current_price - self.b_p_min) / self.b_p_min) + '%' + \
               '\n买入-波动:' + '%0.2f' % (self.current_price - self.last_p) + \
               '\n卖出-波动:' + '%0.2f' % (self.current_price - self.b_p_min) + \
               '\n上次闪动价格:' + str(self.opt_record.get_config_value('last_prompt_point'))[:4]

        debug_print_txt('stk_judge', self.stk_code, str_, self.debug)
        self.add_msg(str_ + '\n')

    def save_opt_info(self):
        """
        将操作日志打印到json
        :return:
        """

        if opt_lock.acquire():
            try:
                opt_record.append({
                    'stk_code': self.stk_code,
                    'p_now': self.current_price,
                    'sale_reseau': self.thh_sale,
                    'buy_reseau': self.thh_buy,
                    'p_last': self.last_p,
                    # 'opt': opt,
                    'date_time': get_current_datetime_str()
                })

            except Exception as e:
                print('函数 JudgeSingleStk:写入操作记录失败！原因：\n' + str(e))

            finally:
                opt_lock.release()

    def cal_reseau(self, rsv):
        """ 调节 buy 和 sale 的threshold """

        """ 实时计算网格大小 """
        earn_threshold_unit = get_single_stk_reseau(self.stk_code)

        rsv.msg = ''
        rsv_stk = rsv.get_stk_rsv(self.stk_code)
        if len(rsv.msg) > 0:
            self.add_msg(rsv.msg + '\n')

        thh_sale = earn_threshold_unit * 2 * rsv_stk
        thh_buy = earn_threshold_unit * 2 * (1 - rsv_stk)

        str_ = '\n卖出网格大小:' + '%0.3f' % thh_sale + '\n买入网格大小:' + '%0.3f' % thh_buy + '\n'
        debug_print_txt('stk_judge', self.stk_code, str_, self.debug)
        self.add_msg(str_)

    def get_pcr(self):
        self.pcr = read_config()['pcr']/100.0

    def bs_info_print(self):
        """
        打印bs信息
        :return:
        """
        # 打印日志
        debug_print_txt('stk_judge', self.stk_code, '读取的最小波动率:' + str(self.pcr) + '\n', self.debug)
        debug_print_txt('stk_judge', self.stk_code, '上次闪动价格:' + str(self.pcr) + '\n', self.debug)

        debug_print_txt('stk_judge', self.stk_code, '允许阈值判断标志位（True为允许）:' + str(self.has_flashed_flag) + '\n', self.debug)
        debug_print_txt('stk_judge', self.stk_code, '判断是否可以卖出：\ncurrent_price - b_p_min > thh_sale:' + str(
            self.current_price - self.b_p_min > self.thh_sale) + '\n', self.debug)
        debug_print_txt('stk_judge', self.stk_code,
                        '(current_price - b_p_min) / b_p_min >= pcr:' + str(
                            (self.current_price - self.b_p_min) / self.b_p_min >= self.pcr) + '\n', self.debug)

        debug_print_txt('stk_judge', self.stk_code,
                        '判断是否可以买入：\ncurrent_price - last_p < -thh_buy:' + str(self.current_price - self.last_p < -self.thh_buy) + '\n',
                        self.debug)

        debug_print_txt('stk_judge', self.stk_code,
                        '(current_price - last_p) / b_p_min <= -pcr:' + str(
                            (self.current_price - self.last_p) / self.b_p_min <= -self.pcr) + '\n', self.debug)

    def fluctuate_judge(self):
        if pd.isnull(self.opt_record.get_config_value('last_prompt_point')):
            return
        elif (self.current_price - self.opt_record.get_config_value('last_prompt_point') > self.thh_sale) &\
                (self.opt_record.get_config_value('last_prompt_point') != -1) &\
                ((self.current_price - self.opt_record.get_config_value('last_prompt_point')) / self.opt_record.get_config_value('last_prompt_point') >= self.pcr):

            str_temp = "当前价格距离上次提示的价格的上涨幅度超过卖出网格！ " + self.stk_code + code2name(self.stk_code) + \
                       '\n当前价格:' + str(self.current_price) + \
                       '\n上次买入价格:' + str(self.b_p_min) + \
                       '\n买入网格大小:' + '%0.3f' % self.thh_buy + \
                       '\n卖出网格大小:' + '%0.3f' % self.thh_sale + \
                       '\n最小操作幅度:' + '%0.3f' % self.pcr + \
                        '\n上次闪动价格:' + str(self.opt_record.get_config_value('last_prompt_point'))[:4]

            self.bs_note(str_temp)

        elif (self.current_price - self.opt_record.get_config_value('last_prompt_point') < -self.thh_buy) &\
                (self.opt_record.get_config_value('last_prompt_point') != -1) &\
                ((self.current_price - self.opt_record.get_config_value('last_prompt_point')) / self.opt_record.get_config_value('last_prompt_point') <= -self.pcr):

            str_temp = "当前价格距离上次提示的价格的下跌幅度超过买入网格！" + self.stk_code + code2name(self.stk_code) + \
                       '\n当前价格:' + str(self.current_price) + \
                       '\n上次价格:' + str(self.last_p) + \
                       '\n买入网格大小:' + '%0.2f' % self.thh_buy + \
                       '\n卖出网格大小:' + '%0.2f' % self.thh_sale + \
                       '\n最小操作幅度:' + '%0.3f' % self.pcr + \
                        '\n上次闪动价格:' + str(self.opt_record.get_config_value('last_prompt_point'))[:4]

            self.bs_note(str_temp)

    def bs_judge(self):

        if (self.current_price - self.b_p_min > self.thh_sale) & ((self.current_price - self.b_p_min) / self.b_p_min >= self.pcr):

            str_temp = "触发卖出网格！可以考虑卖出！ " + self.stk_code + code2name(self.stk_code) + \
                       '\n当前价格:' + str(self.current_price) + \
                       '\n上次买入价格:' + str(self.b_p_min) + \
                       '\n买入网格大小:' + '%0.3f' % self.thh_buy + \
                       '\n卖出网格大小:' + '%0.3f' % self.thh_sale + \
                       '\n最小操作幅度:' + '%0.3f' % self.pcr + \
                        '\n上次闪动价格:' + str(self.opt_record.get_config_value('last_prompt_point'))[:4]

            self.bs_note(str_temp)

        elif (self.current_price - self.last_p < -self.thh_buy) & ((self.current_price - self.last_p) / self.b_p_min <= -self.pcr):

            str_temp = "触发买入网格！可以考虑买入！" + self.stk_code + code2name(self.stk_code) + \
                       '\n当前价格:' + str(self.current_price) + \
                       '\n上次价格:' + str(self.last_p) + \
                       '\n买入网格大小:' + '%0.2f' % self.thh_buy + \
                       '\n卖出网格大小:' + '%0.2f' % self.thh_sale + \
                       '\n最小操作幅度:' + '%0.3f' % self.pcr + \
                        '\n上次闪动价格:' + str(self.opt_record.get_config_value('last_prompt_point'))[:4]

            self.bs_note(str_temp)
        else:
            str_ = self.stk_code + ':未触发任何警戒线！\n'
            self.add_msg(str_)
            debug_print_txt('stk_judge', self.stk_code, str_, self.debug)

    def bs_note(self, str_temp):
        debug_print_txt('stk_judge', self.stk_code, str_temp + '\n在灯神进行bs操作之前，此stk不再进行阈值判断\n',
                        self.debug)

        if not self.has_flashed_flag:
            self.add_note(str_temp)

            # 设置上次闪动价格
            self.opt_record.set_config_value('last_prompt_point', self.current_price)

            # 除非有bs操作，否则不再提示
            self.set_has_flashed_flag(opt_record_file_url, self.stk_code, value=False)

        else:
            self.add_msg(str_temp)



