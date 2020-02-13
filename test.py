from analytics.Analytics import ObluAnalytics
from collections import deque
from time import sleep
import pandas as pd

def tail():
    result = subprocess.run(['tail', '-1', 'sensor/GetData/steps.txt'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


def simulate_data():
    sleep(.20)
    global file
    if not file=="":
        line = file.readline().split(',')
        
        new_X, new_Y = line[1], line[2]
        
        # new_Z = file.readline().split(',')[3]
        new_Z = 0
    else:
        file.seek(0,0)
    return new_X, new_Y

Y = deque(maxlen=200)
oa = ObluAnalytics()

UT, centroid, threshold = oa.getThresholdScore(data_path='sensor/GetData/steps_train.txt')


print(threshold)
test_path = 'sensor/GetData/steps_test.txt'

global file
file = open(test_path, 'r') 
file.readline()

while True:
    Y.append(simulate_data())
    if len(Y) >=200:
        sleep(1)
        print(oa.getScore(UT, centroid, threshold, pd.DataFrame(Y)))

# UT, centroid, threshold = oa.getThresholdScore(data_path=test_path)

# print(threshold)
file.close()