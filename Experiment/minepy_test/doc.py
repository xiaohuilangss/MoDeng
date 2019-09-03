# encoding=utf-8

"""
class minepy.MINE（alpha = 0.6，c = 15，est =“mic_approx” ）
基于最大信息的非参数探索。

参数：

alpha:

(float (0, 1.0] or >=4) – 如果 alpha 在 (0,1] 中，那么B 将会取(n^alpha, 4) 两者之间的最大值，n是样本数量.
 如果 alpha 值 >=4 那么直接将alpha赋值给B。
 .
 如果 alpha 值比样本数量还要多，他会被赋值为样本数量，换句话说，alpha值不会超过样本数量。

c:

(float (> 0)) – determines how many more clumps there will be than columns in every partition.
Default value is 15, meaning that when trying to draw x grid lines on the x-axis, the algorithm will start with at most 15*x clumps.

est:
(str ("mic_approx", "mic_e")) – estimator. With est=”mic_approx” the original MINE statistics will be computed,
with est=”mic_e” the equicharacteristic matrix is is evaluated
and the mic() and tic() methods will return MIC_e and TIC_e values respectively.



compute_score（x，y ）
计算（equi）特征矩阵（即最大归一化互信息分数。

mic（）
返回最大信息系数（MIC或MIC_e）。

mas（）
返回最大不对称分数（MAS）。

mev（）
返回最大边值（MEV）。

mcn（eps = 0 ）
返回eps> = 0的最小单元格编号（MCN）。

mcn_general（）
返回eps = 1 - MIC的最小单元号（MCN）。

gmic（p = -1 ）
返回广义最大信息系数（GMIC）。

tic（norm = False ）
返回总信息系数（TIC或TIC_e）。如果norm == True TIC将在[0,1]中标准化。

get_score（）
返回最大归一化互信息分数（即，如果est =“mic_approx”，
则为特征矩阵M，而不是等特征矩阵）。
M是1d numpy数组的列表，其中M [i] [j]包含使用网格将x值分成i + 2个bin并且y值分成j + 2个bin的分数。

computed（）
如果计算（等于）特征矩阵，则返回True。


"""