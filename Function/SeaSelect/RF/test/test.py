# encoding=utf-8

import tushare as ts


df = ts.get_k_data('300183')

def func(rb):
    print(str(rb))
    return 0

df.loc[:, ['close','high', 'low']].rolling(window=10).apply(func, raw=False)




def answer_question2():
    # 第2题代码写在这里
    _, p_close = w.wsd(['RB.SHF', 'HC.SHF'], 'close', '20160104', '20180830', usedf=True)
    pct = p_close.pct_change().iloc[1:, :]  # 首行为NaN，去除
    rb_shf = pct['RB.SHF']
    hc_shf = pct['HC.SHF']

    # 全局变量，保存滚动回归后的截距
    global_alpha = []

    def rolling_ols(rb):
        '''
        滚动回归，返回滚动回归后的回归系数
        rb: 因变量序列
        '''
        # 数据预处理
        rb.name = 'RB.SHF'
        df = pd.concat([rb, hc_shf], axis=1)  # 方便index对齐
        df.dropna(inplace=True)

        # 回归
        X = sm.add_constant(df['HC.SHF'])
        model = sm.OLS(df['RB.SHF'], X)
        results = model.fit()

        # 结果输出
        global_alpha.append(results.params['const'])
        return results.params['HC.SHF']

    # 滚动回归
    beta = rb_shf.rolling(120).apply(rolling_ols, raw=False)

    # 调整结果输出格式
    beta.dropna(inplace=True)
    beta.name = 'beta'
    global_alpha = pd.Series(global_alpha, index=beta.index, name='alpha')
    res = pd.concat([global_alpha, beta], axis=1)

    return res


ans2 = answer_question2()
print(ans2)