# encoding = utf-8
import pandas as pd
def get_EMA(df,N):
    for i in range(len(df)):
        if i==0:
            df.ix[i,'ema']=df.ix[i,'close']
        if i>0:
            df.ix[i,'ema']=(2*df.ix[i,'close']+(N-1)*df.ix[i-1,'ema'])/(N+1)
    ema=list(df['ema'])
    return ema


def get_MACD(df,short=12,long=26,M=9):
    df = df.reset_index()
    a=get_EMA(df,short)
    b=get_EMA(df,long)
    df['diff']=pd.Series(a)-pd.Series(b)

    for i in range(len(df)):
        if i==0:
            df.ix[i,'dea']=df.ix[i,'diff']
        if i>0:
            df.ix[i,'dea']=(2*df.ix[i,'diff']+(M-1)*df.ix[i-1,'dea'])/(M+1)
    df['MACD']=2*(df['diff']-df['dea'])
    return df

