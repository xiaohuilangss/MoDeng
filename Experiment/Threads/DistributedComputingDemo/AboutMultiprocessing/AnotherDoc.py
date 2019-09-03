import multiprocessing
import time

"""
1、新建单一进程

如果我们新建少量进程，可以如下：
"""
# import multiprocessing
# import time
#
# def func(msg):
#     for i in range(3):
#         print(msg)
#         time.sleep(1)
#
# if __name__ == "__main__":
#     p = multiprocessing.Process(target=func, args=("hello", ))
#     p.start()
#     p.join()
#     print("Sub-process done.")


"""
2、使用进程池

是的，你没有看错，不是线程池。它可以让你跑满多核CPU，而且使用方法非常简单。

注意要用apply_async，如果落下async，就变成阻塞版本了。

processes=4是最多并发进程数量。

"""

# def func(msg):
#     for i in range(3):
#         print(msg)
#         time.sleep(1)
#
#
# if __name__ == "__main__":
#     pool = multiprocessing.Pool(processes=8)
#
#     for i in range(10):
#         msg = "hello %d" % i
#         pool.apply_async(func, (msg, ))
#
#     pool.close()
#     pool.join()
#     print("Sub-process(es) done.")

"""
3、使用Pool，并需要关注结果
更多的时候，我们不仅需要多进程执行，还需要关注每个进程的执行结果，如下：

"""

import multiprocessing
import time

def func(msg):
    for i in range(3):
        print(msg)
        time.sleep(1)
    return "done " + msg


if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=4)
    result = []
    for i in range(10):
        msg = "hello %d" % i
        result.append(pool.apply_async(func, (msg, )))
    pool.close()
    pool.join()
    for res in result:
        print(res.get())
    print("Sub-process(es) done.")