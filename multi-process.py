import os
import time
import pandas as pd
from multiprocessing import Process, Pool
from talib import abstract
from pprint import pp, pprint


def find_best_ma_parameter(src, slow_min, slow_max, fast_max):

    best_winrate = 0
    best_avg_profit = 0
    best_gross_revenue = 0
    best_revenue_fast = 0
    best_revenue_slow = 0
    trading_times = 0

    for slow in range(slow_min, slow_max):
        for fast in range(2*slow, fast_max):
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

            if capital - 1 > best_gross_revenue:
                best_gross_revenue = capital - 1
                best_revenue_fast = fast
                best_revenue_slow = slow
                best_winrate = win_rate
                best_avg_profit = avg_profit
                trading_times = total

    result = dict()
    result['best_avg_profit'] = best_avg_profit
    result['best_winrate'] = best_winrate
    result['trading_times'] = trading_times
    result['best_gross_revenue'] = round(best_gross_revenue, 3)
    result['best_revenue_slow'] = best_revenue_slow
    result['best_revenue_fast'] = best_revenue_fast

    return result


def init_df():
    dict = {'code': '0', 'best_avg_profit': 0, 'trading_times': 0,
            'best_winrate': 0, 'best_gross_revenue': 0,
            'best_revenue_slow': 0, 'best_revenue_fast': 0}
    output = pd.DataFrame([dict]).set_index('code')
    return output


if __name__ == '__main__':
    start_time = time.time()

    output_df = init_df()

    src_list = os.listdir('.\data')

    for src in src_list[:4]:

        result_dict = dict()
        result_dict['code'] = src[:-4]

        result_dict['best_avg_profit'] = 0
        result_dict['best_winrate'] = 0
        result_dict['best_gross_revenue'] = 0
        result_dict['trading_times'] = 0

        pool = Pool(processes=6)
        result = []
        for i in range(12):
            result.append(pool.apply_async(find_best_ma_parameter, args=(src,
                                                                         2*i + 2, 2*i + 4, 250)))

        pool.close()
        pool.join()

        for i in result:
            current_result = i.get()

            if current_result['best_gross_revenue'] > result_dict['best_gross_revenue']:
                result_dict['best_gross_revenue'] = current_result['best_gross_revenue']
                result_dict['best_revenue_fast'] = current_result['best_revenue_fast']
                result_dict['best_revenue_slow'] = current_result['best_revenue_slow']
                result_dict['best_avg_profit'] = current_result['best_avg_profit']
                result_dict['best_winrate'] = current_result['best_winrate']
                result_dict['trading_times'] = current_result['trading_times']

        print('++++++++++++++++++++++++++++++++++++')
        pprint(result_dict)

        # print(f"Stock: {result_dict['code']}")
        # print('-------------')
        # print(
        #     f" Best profit is {best_avg_profit} % \n With slow = {best_profit_slow}, fast = {best_profit_fast}")
        # print(
        #     f" Best winrate is {best_winrate} \n With slow = {best_winrate_slow}, fast = {best_winrate_fast}")
        # print("-------------")
        # print(
        #     f"Best gross revenue is {best_gross_revenue} \n With slow = {best_revenue_slow}, fast = {best_revenue_fast}")
        print("++++++++++++++++++++++++++++++++++++")
        print(f"Time is {time.time() - start_time} s")

        df = pd.DataFrame([result_dict]).set_index('code')
        output_df = output_df.append(df)

    pprint(output_df)
    output_df.to_csv('MA_result.csv')
