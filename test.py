# -*- coding: utf-8 -*-
"""
@File    : 20200318_摄像头多进程流传输.py
@Time    : 2020/3/18 14:58
@Author  : Dontla
@Email   : sxana@qq.com
@Software: PyCharm
"""
import datetime
from multiprocessing import Pool
import time


def test(p):
    time.sleep(1)
    print(datetime.datetime.now())
    return p


if __name__ == "__main__":
    pool = Pool(processes=2)
    result = []
    for i in range(10):

        '''
        for循环执行流程：
        （1）添加子进程到pool，并将这个对象（子进程）添加到result这个列表中。（此时子进程并没有运行）
        （2）执行子进程（同时执行10个）
        '''
        # Dontla 20200319 apply_async()是啥意思？
        # 维持执行的进程总数为10，当一个进程执行完后添加新进程.
        result.append(pool.apply_async(test, args=(i,)))
    pool.close()
    # Dontla 20200319 阻塞主程序等待子进程执行完成
    pool.join()
    '''
    遍历result列表，取出子进程对象，访问get()方法，获取返回值。（此时所有子进程已执行完毕）
    '''
    for i in result:
        print(i.get())
