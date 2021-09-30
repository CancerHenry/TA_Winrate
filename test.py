import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('MA_result.csv')
slow = df['best_revenue_slow']
fast = df['best_revenue_fast']

plt.plot(slow, fast, 'o')

plt.show()
