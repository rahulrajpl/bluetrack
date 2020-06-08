import random
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D


fig = plt.figure()
ax = fig.gca(projection='3d')

plt.style.use('fivethirtyeight')

# x_vals=[]
# y_vals=[]
# z_vals=[]

index = count()

def animate(i):
    # x_vals.append(next(index))
    # y_vals.append(random.randint(0, 5))
    data = pd.read_csv('data.csv')
    x = data['x_value']
    y1 = data['total_1']
    y2 = data['total_2']
    y3 = data['total_3']

    plt.cla()
    # plt.plot(x, y1, label='Channel 1')
    # plt.plot(x, y2, label='Channel 2')
    # plt.plot(x, y3, label='Channel 3')
    plt.plot(y1, y2, y3, label='Random 3D data')
    plt.legend(loc='upper left')
    plt.tight_layout()

ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.tight_layout()
plt.show()
