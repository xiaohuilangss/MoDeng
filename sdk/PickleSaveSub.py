# encoding=utf-8
import pickle
import os


def dumpP(data, saveLocation, fileName):

    with open(saveLocation+fileName, 'wb') as f:
        pickle.dump(data, f)                            # 导入数据data到文件f中
        print('save data: %s successful' % fileName)


def loadP(loadLocation, fileName):

    with open(loadLocation+fileName, 'rb') as f:
        return pickle.load(f)           # 读取数据
