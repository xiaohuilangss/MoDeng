# encodingutf-8

import matplotlib
matplotlib.use('agg')
import jqdatasdk as jq
from CornerDetectAndAutoEmail.Sub import genStkPicForQQ, genStkIdxPicForQQ
from RelativeRank.Sub import get_k_data_JQ

from pylab import *

from SDK.SendMsgByQQ.SendPicByQQ import send_pic_qq


def printStkListPic2QQ(code_list, towho, title=None):

    if title is not None:
        title_str = title
    else:
        title_str = ''

    for x in code_list:
        df = get_k_data_JQ(x, 400)
        fig, _ = genStkPicForQQ(df)

        plt.title(str(x)+title_str)
        send_pic_qq(towho, fig)
        plt.close()

        fig, _ = genStkIdxPicForQQ(df)

        plt.title(str(x)+title_str)
        send_pic_qq(towho, fig)
        plt.close()


def sendBillBoardPic2QQ():

    df_today = jq.get_billboard_list(start_date='2019-06-21')

    abnor_list = list(df_today.groupby(by='abnormal_name'))

    # 打印4类
    df_duplicate_4 = abnor_list[4][1].loc[~abnor_list[4][1]['code'].duplicated(), :]
    code_list_4 = [x[:6] for x in list(df_duplicate_4['code'].values)]

    printStkListPic2QQ(code_list_4, '影子', title=abnor_list[4][0])

    # 打印1类
    df_duplicate_1 = abnor_list[1][1].loc[~abnor_list[1][1]['code'].duplicated(), :]
    code_list_1 = [x[:6] for x in list(df_duplicate_1['code'].values)]

    printStkListPic2QQ(code_list_1, '影子', title=abnor_list[1][0])


if __name__ == '__main__':

    # from JQData_Test.auth_info import *

    sendBillBoardPic2QQ()

    end = 0