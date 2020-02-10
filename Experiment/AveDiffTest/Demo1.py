# encoding=utf-8
"""
展示Reseau结果
"""
from ReseauTest.Sub import SingleReseauJudge
import tushare as ts
from pylab import *

from SDK.Normalize import normal01
from SDK.PlotOptSub import add_axis

mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False

if __name__ == '__main__':

    """ ----------------------- 准备训练数据 ------------------------------  """
    stk_code = 'cyb'
    sh_index = ts.get_k_data(code=stk_code, start='2014-01-01')

    sh_index['M20'] = sh_index['close'].rolling(window=180, center=False).mean()
    sh_index['M5'] = sh_index['close'].rolling(window=30, center=False).mean()
    sh_index['M5-M20'] = sh_index.apply(lambda x: x['M5'] - x['M20'], axis=1)

    sh_index['MM9'] = sh_index['M5-M20'].rolling(window=5, center=False).mean()
    sh_index['MACD'] = sh_index.apply(lambda x: x['M5-M20'] - x['MM9'], axis=1)

    sh_index = sh_index.dropna(how='any')

    """ -------------------------------- 图示结果 ------------------------------------ """
    fig, ax = plt.subplots(nrows=2, ncols=1)
    ax[0].plot(range(len(sh_index['date'])), sh_index['close'], 'b--')
    # ax[0].plot(range(len(sh_index['date'])), sh_index['M5-M20'], 'r--')

    ax[1].plot(range(len(sh_index['date'])), sh_index['MACD'], 'r--')

    # 整理x轴label
    x_label = sh_index.apply(lambda x: str(x['date'])[2:].replace('-', ''), axis=1)

    ax[0] = add_axis(ax[0], x_label, 40, rotation=45, fontsize=8)
    ax[1] = add_axis(ax[1], x_label, 40, rotation=45, fontsize=8)
    # ax[2] = addXticklabel(ax[2], x_label, 40, rotation=45, fontsize=8)
    # ax[3] = addXticklabel(ax[3], x_label, 40, rotation=45, fontsize=8)

    for ax_sig in ax:
        ax_sig.legend(loc='best')

    plt.show()

end = 0