import subprocess
import os

def tail():
    result = subprocess.run(['tail', '-1', 'data.csv'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8') 

print(tail())