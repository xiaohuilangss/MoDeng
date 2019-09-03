# encoding = utf-8

# from General.GlobalSetting import *
from SDK.SDKHeader import *
from PyEMD import EMD
import numpy as np
import pylab as plt
from scipy import fftpack

mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False

# 准备数据
stk_df = get_total_table_data(conn_k, 'k300508')
s = np.array(stk_df.close)
x_axis = range(0, len(s))

# 定义信号
# t = np.linspace(0, 1, 200)
# s = np.cos(11*2*np.pi*t*t) + 6*t*t

# 对信号执行emd
IMF = EMD().emd(s)
N = IMF.shape[0]+1

# 图示结果
plt.subplot(N+1, 1, 1)
plt.plot(x_axis, s, 'r')
# plt.title("原始数据")

# 求取第一个imf的希尔伯特变换# plt.xlabel("日期")
ht = fftpack.hilbert(IMF[0])

plt.subplot(N+1, 1, 2)
plt.plot(x_axis, ht)


for n, imf in enumerate(IMF):
    plt.subplot(N+1, 1, n+3)
    plt.plot(x_axis, imf, 'g')
    # plt.title("IMF "+str(n+1))
    # plt.xlabel("日期")

# plt.tight_layout()
# plt.savefig('simple_example')
plt.show()
end = 0
