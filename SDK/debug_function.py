# encoding=utf-8
import time


def print_run_time(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        r = func(*args, **kw)
        print('函数 [%s] 共运行耗时 %.2f 秒！' % (func.__name__, time.time() - local_time))
        return r
    return wrapper


if __name__ == '__main__':
    pass
