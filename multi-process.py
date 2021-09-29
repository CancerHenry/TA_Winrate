import os
import time
import pandas as pd
from multiprocessing import Process, Pool
from talib.abstract import *
from pprint import pprint

# src_list = os.listdir('.\data')


def find_best_ma_parameter(slow_min, slow_max, fast_max):
    src_list = ['sh.000001.csv']

    for src in src_list:

        best_winrate = 0
        best_avg_profit = 0

        best_profit_fast = 0
        best_profit_slow = 0

        best_winrate_fast = 0
        best_winrate_slow = 0

        best_gross_revenue = 0
        best_revenue_fast = 0
        best_revenue_slow = 0

        for slow in range(slow_min, slow_max):
            for fast in range(2*slow, fast_max):
                stock = pd.read_csv(f'.\data\{src}')
                open = stock['open']
                high = stock['high']
                low = stock['low']
                close = stock['close']

                stock['SMA_s'] = SMA(close, timeperiod=slow)
                stock['SMA_f'] = SMA(close, timeperiod=fast)

                # Delete data with NaN values
                stock = stock[stock['SMA_s'].notna()]

                total = 0
                success = 0
                fail = 0
                in_position = False
                total_profit_percent = 0
                capital = 1

                for index, value in stock[1:].iterrows():
                    this_SMA_f = value['SMA_f']
                    this_SMA_s = value['SMA_s']
                    last_SMA_f = stock.loc[index - 1]['SMA_f']
                    last_SMA_s = stock.loc[index - 1]['SMA_s']

                    if last_SMA_f <= last_SMA_s and this_SMA_f > this_SMA_s and not in_position:
                        in_price = value['close']
                        in_position = True

                    if last_SMA_f >= last_SMA_s and this_SMA_f < this_SMA_s and in_position:
                        total += 1
                        in_position = False
                        out_price = value['close']
                        profit = out_price - in_price
                        if profit > 0:
                            success += 1
                        else:
                            fail += 1

                        profit_percent = round((profit / in_price) * 100, 3)

                        capital *= (1 + profit_percent / 100)

                        total_profit_percent += profit_percent

                avg_profit = round(total_profit_percent / total, 3)
                win_rate = round(success / total, 3)

                if avg_profit > best_avg_profit:
                    best_avg_profit = avg_profit
                    best_profit_fast = fast
                    best_profit_slow = slow

                if win_rate > best_winrate:
                    best_winrate = win_rate
                    best_winrate_fast = fast
                    best_winrate_slow = slow

                if capital - 1 > best_gross_revenue:
                    best_gross_revenue = capital - 1
                    best_revenue_fast = fast
                    best_revenue_slow = slow

    result = dict()
    result['best_avg_profit'] = best_avg_profit
    result['best_profit_slow'] = best_profit_slow
    result['best_profit_fast'] = best_profit_fast
    result['best_winrate'] = best_winrate
    result['best_winrate_slow'] = best_winrate_slow
    result['best_winrate_fast'] = best_winrate_fast
    result['best_gross_revenue'] = best_gross_revenue
    result['best_revenue_slow'] = best_revenue_slow
    result['best_revenue_fast'] = best_revenue_fast

    return result


if __name__ == '__main__':
    start_time = time.time()

    pool = Pool(processes=4)
    result = []
    for i in range(8):
        result.append(pool.apply_async(find_best_ma_parameter, args=(
            i + 2, i + 3, 15)))

    pool.close()
    pool.join()

    for i in result:
        print(i.get())

    print(f'Time is {time.time() - start_time} s')
