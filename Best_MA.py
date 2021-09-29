import os
import time
import pandas as pd
from talib import abstract

#src_list = os.listdir('.\data')

src_list = ['sh.000001.csv']

for src in src_list:

    start = time.time()

    best_winrate = 0
    best_avg_profit = 0

    best_profit_fast = 0
    best_profit_slow = 0

    best_winrate_fast = 0
    best_winrate_slow = 0

    best_gross_revenue = 0
    best_revenue_fast = 0
    best_revenue_slow = 0

    for slow in range(2, 15):
        for fast in range(2*slow, 35):
            stock = pd.read_csv(f'.\data\{src}')
            open = stock['open']
            high = stock['high']
            low = stock['low']
            close = stock['close']

            stock['SMA_s'] = abstract.SMA(close, timeperiod=slow)
            stock['SMA_f'] = abstract.SMA(close, timeperiod=fast)

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

            print(f'Slow = {slow}, Fast = {fast}')
            print(f"Total trading times is {total}")
            print(f'Win rate is {win_rate}')
            print(f'Average profit is {avg_profit} %')
            print('-------------------------------')

    duration = round(time.time() - start, 2)
    print(f'Time used is {duration} s')

    print('++++++++++++++++++++++++++++++++++++')
    print(f'Stock: {src[:-4]}')
    print('-------------')
    print(
        f' Best profit is {best_avg_profit} % \n With slow = {best_profit_slow}, fast = {best_profit_fast}')
    print(
        f' Best winrate is {best_winrate} \n With slow = {best_winrate_slow}, fast={best_winrate_fast}')
    print('-------------')
    print(
        f'Best gross revenue is {best_gross_revenue} \n With slow = {best_revenue_slow}, fast = {best_revenue_fast}')
    print('++++++++++++++++++++++++++++++++++++')
