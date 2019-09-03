import multiprocessing as mp
import threading as td
import time

""" ====================================================================== """

# def job(q):
#     res = 0
#     for i in range(100000):
#         res += i + i ** 2
#     q.put(res)
#
#
# def normal():
#     res = 0
#     for i in range(100000):
#         res += i + i ** 2
#     print('normal:', res)
#
#
# def multithread():
#     q = mp.Queue()  # 这里用多进程的queue没问题的
#     t1 = td.Thread(target=job, args=(q,))
#     #     t2 = td.Thread(target = job(q,))
#     t1.start()
#     #     t2.start()
#     t1.join()
#     #     t2.join()
#     res1 = q.get()
#     #     res2 = q.get()
#     print('thread:', res1)
#
#
# def multiprocess():
#     q = mp.Queue()
#     p1 = mp.Process(target=job, args=(q,))
#     #     p2 = mp.Process(target = job(q,))
#     p1.start()
#     #     p2.start()
#     p1.join()
#     #     p2.join()
#     res1 = q.get()
#     #     res2 = q.get()
#     print('multiprocess:', res1)
#
#
# if __name__ == '__main__':
#     st = time.time()
#     normal()
#     st1 = time.time()
#     print('normal time:', st1 - st)
#
#     multithread()
#     st2 = time.time()
#     print('thread:', st2 - st1)
#
#     multiprocess()
#     print('process:', time.time() - st2)


""" ====================================================================== """
# 进程池 ,Pool中是有return的
import multiprocessing as mp


def job(x):
    return x ** 2


def multiprocess():
    pool = mp.Pool()                    # 默认是有几个核就用几个，可以自己设置processes = ？
    res = pool.starmap(job, range(10))      # 可以放入可迭代对象，自动分配进程
    print(res)

    res = pool.apply_async(job, (2,))  # 一次只能在一个进程里计算，要达到map的效果，要迭代
    print(res.get())

    multi_res = [pool.apply_async(job, (i,)) for i in range(10)]  # 迭代器
    print([res.get() for res in multi_res])


if __name__ == '__main__':
    multiprocess()