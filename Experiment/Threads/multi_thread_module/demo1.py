# encoding = utf-8

"""

"""

# -*- coding: utf-8 -*-
# coding=utf-8
import codecs
import logging
import multiprocessing
import time

from queue import Queue, Empty

thread_mode = 'thread'
process_mode = 'process'
async_mode = 'async'
network_mode = 'machine'

## https://github.com/ferventdesert/multi_yielder


class Stop(Exception):
    "a flag when queue should stop"
    pass


class Yielder(object):
    ''' a yield context manager '''
    def __init__(self, dispose):
        self.dispose = dispose

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()


def safe_queue_get(queue, is_stop_func=None, timeout=2):
    while True:
        if is_stop_func is not None and is_stop_func():
            return Stop
        try:
            data = queue.get(timeout=timeout)
            return data
        except:
            continue


def safe_queue_put(queue, item, is_stop_func=None, timeout=2):
    while True:
        if is_stop_func is not None and is_stop_func():
            return Stop
        try:
            queue.put(item, timeout=timeout)
            return item
        except:
            continue


def multi_yield(generator, customer_func, mode=thread_mode, worker_count=2, queue_size=10):
    """
    :param generator:  a iter object offer task seeds, can be array, generator
    :param customer_func:  your task func, get seed as parameter and yield result, if no result needed, yield None
    :param mode: three support mode: thread, gevent, process
    :param worker_count:
    :param queue_size:
    :return: a result generator
    """
    workers = []

    def is_alive(process):
        if mode == process_mode:
            return process.is_alive()
        elif mode == thread_mode:
            return process.isAlive()
        return True

    class Stop_Wrapper():
        def __init__(self):
            self.stop_flag = False
            self.workers = []

        def is_stop(self):
            return self.stop_flag

        def stop(self):
            self.stop_flag = True
            for process in self.workers:
                if isinstance(process, multiprocessing.Process):
                    process.terminate()

    stop_wrapper = Stop_Wrapper()

    def _boss(task_generator, task_queue, worker_count):
        for task in task_generator:
            item = safe_queue_put(task_queue, task, stop_wrapper.is_stop)
            if item is Stop:
                print('downloader boss stop')
                return
        for i in range(worker_count):
            task_queue.put(Empty)
        print('worker boss finished')

    def _worker(task_queue, result_queue, gene_func):
        import time
        try:
            while not stop_wrapper.is_stop():
                if task_queue.empty():
                    time.sleep(0.01)
                    continue
                task = safe_queue_get(task_queue, stop_wrapper.is_stop)
                if task == Empty:
                    result_queue.put(Empty)
                    break
                if task == Stop:
                    break
                for item in gene_func(task):
                    item = safe_queue_put(result_queue, item, stop_wrapper.is_stop)
                    if item == Stop:
                        break
            print('worker worker is stop')
        except Exception as e:
            logging.exception(e)
            print('worker exception, quit')

    def factory(func, args=None, name='task'):
        if args is None:
            args = ()
        if mode == process_mode:
            return multiprocessing.Process(name=name, target=func, args=args)
        if mode == thread_mode:
            import threading
            t = threading.Thread(name=name, target=func, args=args)
            t.daemon = True
            return t
        if mode == async_mode:
            import gevent
            return gevent.spawn(func, *args)

    def queue_factory(size):
        if mode == process_mode:
            return multiprocessing.Queue(size)
        elif mode == thread_mode:
            return Queue(size)
        elif mode == async_mode:
            from gevent import queue
            return queue.Queue(size)

    def should_stop():
        if not any([r for r in workers if is_alive(r)]):
            return True
        return stop_wrapper.is_stop()

    with Yielder(stop_wrapper.stop):
        result_queue = queue_factory(queue_size)
        task_queue = queue_factory(queue_size)

        main = factory(_boss, args=(generator, task_queue, worker_count), name='_boss')
        for process_id in range(0, worker_count):
            name = 'worker_%s' % process_id
            p = factory(_worker, args=(task_queue, result_queue, customer_func), name=name)
            workers.append(p)
        main.start()
        stop_wrapper.workers = workers[:]
        stop_wrapper.workers.append(main)
        for r in workers:
            r.start()
        count = 0
        while not should_stop():
            data = safe_queue_get(result_queue, should_stop)
            if data is Empty:
                count += 1
                if count == worker_count:
                    break
                continue
            if data is Stop:
                break
            else:
                yield data


if __name__ == '__main__':

    def xprint(x):
        """
        mock a long time task
        """
        time.sleep(1)
        yield x * x


    i = 0
    for item in multi_yield(range(100), xprint, process_mode, 3):
        print(item)
        i += 1
        if i > 10:
            break