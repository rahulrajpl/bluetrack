from analytics.Analytics import ObluAnalytics
from collections import deque
from time import sleep
import pandas as pd

def tail():
    result = subprocess.run(['tail', '-1', 'sensor/GetData/steps.txt'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


def simulate_data():
    sleep(1)
    global file
    if not file=="":
        new_X = file.readline().split(',')[1]
        new_Y = file.readline().split(',')[2]
        # new_Z = file.readline().split(',')[3]
        new_Z = 0
    else:
        file.seek(0,0)
    return new_X, new_Y, new_Z

Y = deque(maxlen=20)
oa = ObluAnalytics()

UT, centroid, threshold = oa.getThresholdScore(data_path='sensor/GetData/steps_train.txt')


print(threshold)
test_path = 'sensor/GetData/steps_test.txt'

global file
file = open(test_path, 'r') 
file.readline()

while True:
    Y.append(simulate_data())
    if len(Y) >=20:
        print(oa.getScore(UT, centroid, threshold, pd.DataFrame(Y)))
