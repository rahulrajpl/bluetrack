import subprocess
import os
from time import sleep

def tail():
    result = subprocess.run(['tail', '-1', 'sensor/steps.txt'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8') 

while True:
    sleep(1)
    x = str(tail()).split(',')[1]
    y = str(tail()).split(',')[2]

    print(f'x={x} and y={y}')