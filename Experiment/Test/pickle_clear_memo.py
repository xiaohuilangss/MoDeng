# encoding=utf-8

import pickle
from sdk.PickleSaveSub import dumpP, loadP

import pandas as pd
import pandas_profiling
import tushare as ts
import json

# df = ts.get_k_data('000001')

with open("C:/rf_sea_select/1d/total.json", 'r') as f:
    df = pd.DataFrame(json.load(f))

pandas_profiling.ProfileReport(df.head(10000))
profile = df.profile_report(title="oil_data")
profile.to_file(output_file="oil_data.html")

a = [1, 2, 3]
b = [4, 5, 6]

dumpP(a, './', 'test')

r1 = loadP('./', 'test')

dumpP(b, './', 'test')

r2 = loadP('./', 'test')

end = 0


def Load():
    d = {}
    with open('test.txt', 'rb') as f:
        while True:
            try:
                a = pickle.load(f)
            except EOFError:
                break
            else:
                d.update(a)