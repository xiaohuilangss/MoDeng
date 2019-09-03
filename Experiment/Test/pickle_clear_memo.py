# encoding=utf-8

import pickle

from SDK.PickleSaveSub import dumpP, loadP

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