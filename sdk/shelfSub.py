# encoding=utf-8
import shelve


def shelveP(data, saveLocation, fileName):

    s = shelve.open(saveLocation+fileName, writeback=True)

    try:
        s['key1'] = data
        print('save data: %s successful' % fileName)  # 导入数据data到文件f中
    finally:
        s.close()


def shelveL(loadLocation, fileName):

    s = shelve.open(loadLocation+fileName, flag='r')
    try:
        existing = s['key1']
    finally:
        s.close()

    return existing


if __name__ == '__main__':

    # shelveP([1, 3, 5, 3], './', 'test')

    r = shelveL('./', 'test')
    end=0