# encoding = utf-8

"""
在关心的stk中，计算其24个月的水平，并按高低排序，画出柱状图
"""
from Config.Sub import readConfig
# from MACD_Stray_Analysis.Demo1 import calStkPlevel
# from RelativeRank.Sub import get_k_data_JQ
from Experiment.MACD_Stray_Analysis.Sub import cal_stk_p_level
from Experiment.RelativeRank.Sub import get_k_data_JQ
from sdk.MyTimeOPT import add_date_str, get_current_date_str

from pylab import *

from HuiCe.Sub import code2name_dict
from sdk.send_msg_by_qq.QQGUI import send_qq
from sdk.send_msg_by_qq.SendPicByQQ import send_pic_qq



def sendRelaLevel2QQ():
    send_qq(towho='影子2', msge='注意低位囤货：')
    calRelaPLevel(readConfig()['safe_stk'], -720, '影子2')


def sendPLevel2QQ(df, towho):
    """
    将stk的价格水平发送到qq
    :df: code, level
    :return:
    """

    r_df = df

    # 按level从低到高进行排序
    r_df_sort = r_df.sort_values(by='level', ascending=True).head(12)

    fig, ax = plt.subplots(ncols=1, nrows=1)

    ax.bar(range(0, len(r_df_sort)), r_df_sort['level'])
    # ax.plot(range(0, len(r_df_sort)), [0.1 for x in r_df_sort['level']], 'r--')
    # ax.plot(range(0, len(r_df_sort)), [0.5 for x in r_df_sort['level']], 'r--')

    # 获取code2name字典
    c2n = code2name_dict()

    ax.set_xticks(range(0, len(r_df_sort)))
    ax.set_xticklabels([c2n[x] for x in r_df_sort['code']], rotation=45)

    plt.ylim((0, 1))
    plt.grid()
    plt.title('注意低位囤货！')
    send_pic_qq(towho, fig)
    plt.close()


def calRelaPLevel(stk_list, period, towho):
    """
    计算相对价格，并发送到qq
    :param stk_list:
    :return:
    """

    r = [
        (x, cal_stk_p_level(np.array(get_k_data_JQ(stk_code=x, start_date=add_date_str(get_current_date_str(), period))['close']))['total_last'])
        for x in stk_list]
    r_df = pd.DataFrame(data=r, columns=['code', 'level'])

    sendPLevel2QQ(r_df, towho)


if __name__ == '__main__':

    from DataSource.auth_info import *
    calRelaPLevel(['300508', '000001'])