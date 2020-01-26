import subprocess
import os
from time import sleep

def readline():
    file = open('sensor/GetData/steps.txt', 'r') 
    file.readline()
    while True:
        sleep(1)
        print(file.readline())
        # result = subprocess.run(['tail', '-1', 'sensor/steps.txt'], stdout=subprocess.PIPE)
        # return result.stdout.decode('utf-8') 

readline()