# encoding = utf-8

import tushare as ts
import tensorflow as tf

df_stk = ts.get_k_data('000001',start='2011-01-01')

standard_price = df_stk.head(1)['close'].values[0]            # 基准价格
sale_ratio = 0.01                   # 卖出涨幅
buy_ratio = -0.01                   # 买入跌幅

capital = 50000                     # 总资本
capital_available = 10000           # 可用资本
wager_inc_ratio = 1                 # 补仓倍数
wager_now = 300                     # 当前补仓量
wager_amount = 3000                 # 当前持仓股数

market_value = 0                    # 当前市值
cost = wager_amount*standard_price  # 当前成本
profit = 0                          # 总利润

last_opt = True                     # true 表示上次是买，false表示上次是卖

tax = 0.0025

ad_trend = 1.2      # 应对连涨连跌情况

for id in df_stk.index:

    date = df_stk.loc[id,'date']
    price_now = df_stk.loc[id,'close']



    # ------------------------------------ 跌了买 -----------------------------------------

    if (price_now - standard_price)/standard_price < buy_ratio:

        # ----------------------------------- 更新买卖阈值 ------------------------------------
        if last_opt:
            buy_ratio = buy_ratio * ad_trend
            sale_ratio = 0.01
        else:
            buy_ratio = -0.01
            sale_ratio = sale_ratio * ad_trend


        last_opt = True

        # 计算本次被操作的赌注大小
        wager_opt_amount = wager_now * wager_inc_ratio

        # 判断成本是否超过本金
        if cost + price_now*wager_opt_amount < capital:

            # 更新成本
            cost = cost + price_now*wager_opt_amount*(1+tax)

            # 更新持仓股数
            wager_amount = wager_amount + wager_opt_amount

            print('\n基准价格：'+str(standard_price) + '当前价格：'+str(price_now) + '进行买入操作！买入数量：' + str(wager_now), '当前买入跌幅阈值为：' + str(buy_ratio) + '可用资金：' + str(capital - cost))

            # 更新基准价格
            standard_price = price_now
        else:
            print('无资金增援！')

    # -------------------------- 涨了卖 ----------------------------------------------------
    elif (price_now - standard_price)/standard_price > sale_ratio:

        # ----------------------------------- 更新买卖阈值 ------------------------------------
        if last_opt:
            buy_ratio = buy_ratio * ad_trend
            sale_ratio = 0.01
        else:
            buy_ratio = -0.01
            sale_ratio = sale_ratio * ad_trend

        last_opt = False

        # 计算本次被操作的赌注大小
        wager_opt_amount = wager_now*wager_inc_ratio

        # 判断是否有足够stk可卖
        if wager_amount > wager_opt_amount:

            # 更新成本
            cost = cost - wager_opt_amount*price_now*(1-tax)

            # 更新持仓股数
            wager_amount = wager_amount - wager_opt_amount

            print('\n基准价格：' + str(standard_price) + '当前价格：' + str(price_now) + '进行卖出操作！卖出数量：' + str(wager_now), '当前卖出增幅阈值为：' + str(sale_ratio))

            # 更新基准价格
            standard_price = price_now
        else:
            print('无筹码可卖！')

            # 更新基准价格
            standard_price = price_now

    # 更新持仓市值
    market_value = wager_amount * price_now

    # 更新利润
    profit = market_value - cost

    print('当前利润：'+str(profit) + '\t当前市值：' + str(market_value) + '\t当前成本：' + str(cost) + '\t当前持股数：' + str(wager_amount) + '\t当前下注大小：' + str(wager_now))

end = 0