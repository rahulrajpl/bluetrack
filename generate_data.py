import csv
import random
import time

x_value = 0
total_1 = 0
total_2 = 0
total_3 = 0

fieldnames = ["x_value", "total_1", "total_2", "total_3"]

with open('data.csv', 'w') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()

while True:
    with open('data.csv', 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        info = {
            'x_value' : x_value,
            'total_1' : total_1,
            'total_2' : total_2,
            'total_3' : total_3,
        }

        csv_writer.writerow(info)
        print(x_value, total_1, total_2, total_3)

        x_value += 1
        
        # if total_1 < 80 or total_2 < 80:
        total_1 += random.randint(0, 1)
        total_2 += random.randint(0, 1)
        total_3 += random.randint(0, 2)
        # else:
        #     total_1 = 1
        #     total_2 = 1


    time.sleep(1)
