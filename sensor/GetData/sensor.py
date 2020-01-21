# -*- coding: utf-8 -*-
'''
  Copyright (C) 2018 GT Silicon Pvt Ltd

  Licensed under the Creative Commons Attribution 4.0
  International Public License (the "CCBY4.0 License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  https://creativecommons.org/licenses/by/4.0/legalcode

#  It stop running program (ObluIot.py) by using below command
#   python sensor.py stop

# Change the ip address before running the script
# Use sensor.py to stop this running programm properly e.g.
#    python sensor.py stop

#Authors: Ajit Gupta

#
#     Date     |    Review    |      Author                      |  Comments
# -------------+--------------+-----------------------------------------------------
#   10-05-2018 |    0.0       |   Ajit Gupta                     | Intial Version
'''

import sys

command_usage = "./sensor.py stop/shutdown"
if __name__ == '__main__':
    print (sys.argv)
    command = sys.argv[1].strip()

    if  len(sys.argv) < 2  :
        print (command_usage)
    else :
        if (command.lower() == 'stop' or command.lower() == 'shutdown'):
            with open('command.txt', 'w') as the_file:
                the_file.write(' '.join(sys.argv[1:]) + "\n")
        else:
            print (command_usage)


