# encoding=utf-8

""" 本脚本包含lstm训练所需要的各种参数 """

# feature_cols = ['M21pre', 'MACD', 'RSI12', 'RSI30', 'SAR', 'slowk', 'slowd', 'close', 'high', 'low', 'volume']
feature_cols = ['open', 'close', 'high', 'low', 'volume', 'rank']
label_col = ['high']

stk_code = 'cyb'
M_INT = 21

N_STEPS = 20
N_INPUTS = 9
HIDDEN_SIZE = 12
NUM_LAYERS = 2