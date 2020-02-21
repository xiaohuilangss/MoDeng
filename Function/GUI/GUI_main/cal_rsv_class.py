# encoding=utf-8
from Config.Sub import read_config
from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_k_data_JQ
from Global_Value.p_diff_ratio_last import RSV_Record
from SDK.Debug_Sub import debug_print_txt
from SDK.MyTimeOPT import get_current_date_str


class RSV:
    def __init__(self):
        self.rsv = {}
        self.update_success = self.update_rsv_record()
        self.msg = ''

    def update_rsv_record(self):

        try:
            code_list = list(
                set(read_config()['buy_stk'] + read_config()['concerned_stk'] + read_config()['index_stk']))

            # global  RSV_Record
            for stk in code_list:
                self.rsv[stk] = self.cal_stk_rsv_rank(stk, 5)

            return True

        except Exception as e:
            print(str(e))
            self.msg = 'RSV数据更新失败！原因：\n' + str(e)
            debug_print_txt('main_log', '', 'RSV数据更新失败！原因：\n' + str(e) + '\n')

            return False

    @staticmethod
    def add_rsv(df, m, debug=False):
        """
        向df中增加rsv数据
        :return:
        """
        # 移动平均线+RSV（未成熟随机值）
        df['low_M' + str(m)] = df['low'].rolling(window=m).mean()
        df['high_M' + str(m)] = df['high'].rolling(window=m).mean()
        df['close_M' + str(m)] = df['close'].rolling(window=m).mean()

        debug_print_txt('rsv_cal', '', df.to_string(), debug)

        for idx in df.index:
            if (df.loc[idx, 'high_M' + str(m)] - df.loc[idx, 'low_M' + str(m)] == 0) | (
                    df.loc[idx, 'close_M' + str(m)] - df.loc[idx, 'low_M' + str(m)] == 0):
                df.loc[idx, 'RSV'] = 0.5

                debug_print_txt('rsv_cal', '', '最高点均值-最低点均值=0,近日可能无波动，rsv设置为0.5', debug)

            else:
                df.loc[idx, 'RSV'] = (df.loc[idx, 'close_M' + str(m)] - df.loc[idx, 'low_M' + str(m)]) / (
                        df.loc[idx, 'high_M' + str(m)] - df.loc[idx, 'low_M' + str(m)])
        return df

    @staticmethod
    def cal_rsv_rank_sub(df, m):
        """
        独立这一函数，主要是为了huice
        :param df:
        :param m:
        :return:
        """

        df = RSV.add_rsv(df, m)

        return df.tail(1)['RSV'].values[0]

    def cal_stk_rsv_rank(self, stk_code, m_days, history_length=400, debug=False):

        df = get_k_data_JQ(stk_code, count=history_length, end_date=get_current_date_str())

        debug_print_txt('rsv_cal', '', code2name(stk_code) + '开始计算rsv:', debug)

        rsv = self.cal_rsv_rank_sub(df, m_days)

        debug_print_txt('rsv_cal', '', '最终rsv：' + '%0.3f' % rsv, debug)

        return rsv

    def get_stk_rsv(self, stk_code):
        """
        获取一只股票的RSV
        :return:
        """

        if stk_code in self.rsv.keys():
            return self.rsv[stk_code]
        else:
            self.msg = stk_code + code2name(stk_code) + 'rsv值不存在，临时下载！'
            rsv = self.cal_stk_rsv_rank(stk_code, 5)
            self.rsv[stk_code] = rsv
            return rsv

