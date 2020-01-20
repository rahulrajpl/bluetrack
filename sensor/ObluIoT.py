# -*- coding: utf-8 -*-
'''
  Copyright (C) 2018 GT Silicon Pvt Ltd

  Licensed under the Creative Commons Attribution 4.0
  International Public License (the "CCBY4.0 License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  https://creativecommons.org/licenses/by/4.0/legalcode
'''
#  It covered below functionality.
#  - Connect to oblu sensor
#  - TCP/IP communication with oblu sensor using socket programming
#  - Receive oblu’s location data and processing it
#  - Display the location data in below format and also write it to file(steps.txt)
#     StepNumber, X, Y, Z, orientation


# Change the ip address before running the script
# Use sensor.py to stop this running programm properly e.g.
#    python sensor.py stop

#Authors: Ajit Gupta

#
#     Date     |    Review    |      Author                      |  Comments
# -------------+--------------+-----------------------------------------------------
#   10-05-2018 |    0.0       |   Ajit Gupta                     | Intial Version
#   06-06-2018 |    0.0       |   Ajit Gupta                     | TCP/IP communication with oblu


import Queue
import struct
import math
import re
import time
import os
import datetime
import threading
import socket
import sys
import traceback
import thread

# device_ip = '172.31.5.214'
# device_ip = '192.168.43.201'
# device_ip = '192.168.1.5'


# device_ip = '172.27.22.120' # No 149
device_ip = '172.27.22.57' # No 145

MAX_CMD_LENGTH = 6
ACK_LEN = 4
PACKET_LEN = 64
# START_CMD = "340034"
START_CMD = "340034"
SYS_OFF_CMD = "220022"
PROC_OFF_CMD = "320032"
LOG_FILE = "steps.txt" #check in powershell, > Get-Content -Path "C:/xampp/htdocs/iot_single/steps" -Wait
TIME_OUT = 10
NUM_RETRY = -1
g_isRunning = True
queue = Queue.Queue()

def monitorUserCmd():
    global g_isRunning
    seq = 0
    while True:
        command = ''
        try:
            with open("command.txt", "r") as f:
                for line in f:
                    if len(line.strip()) > 0:
                        command = line.strip().split()
                        print "Command received : " + line.strip()
                        break
        except IOError:
            pass
        open('command.txt', 'w').close()
        if len(command) > 0 and command[0].lower() == 'stop':
            g_isRunning = False
            break
        time.sleep(5)


def putDataToCloud(data_queue):
    global g_isRunning
    # Firebase Cloud Initilization
    while g_isRunning:
        while not data_queue.empty():
            data =  data_queue.get()
            # Put data to Firebase Database
            print data
            ##############################################
            data_queue.task_done()
        time.sleep(1)


class DeviceConnectivityError(RuntimeError):
   def __init__(self, arg):
      self.args = arg

class DeviceClient(threading.Thread):
    client_socket = ''
    outfile = ''
    def __init__(self, name, ip, port, queue):
        threading.Thread.__init__(self)
        self.host = ip
        self.port = port
        self.pkt_counter = 0
        self.last_ack = ''
        self.filename = name
        self.queue = queue
        self.prev_x = -1
        self.prev_y = -1
        self.prev_z = 0

    def open_device(self, host, port):
        print "Connecting to device", host
        client_socket = socket.socket()
        client_socket.connect((host, port))  # connect to the server
        return client_socket

    def read_device(self, length):
        device_data = ''
        # client_socket.flushInput()
        data_len = 0

        while data_len < length:
            try:
                device_data += self.client_socket.recv(length - data_len)
                data_len += len(device_data)
                if data_len < length:
                    time.sleep(0.05)
            except socket.error:
                if self.IsDeviceActive() == False:
                    raise DeviceConnectivityError("Device is not active")
        return device_data

    def write_device(self, device_data):
        isSendData = False
        while isSendData != True:
            try:
                self.client_socket.send(device_data)
                isSendData = True
            except socket.error:
                isSendData = False
                print "write_device: Sending Failure"
                if self.IsDeviceActive() == False:
                    raise DeviceConnectivityError("Device is not active")

    def parse_pkt(self, device_data):
        pkt_info = ()
        payload = []
        # print buffer
        try:
            (start_code, pkt_num1, pkt_num2, payload_length) = struct.unpack("!BBBB", device_data[0:4])

            if start_code != 0xAA:
                # print "Error: Failed to detect header at packet start, data=" + device_data.encode("hex")
                # valid = False
                raise Exception("Failed to detect header at packet start, data=" + device_data.encode("hex"))
            else:
                valid = True
                (step_count, checksum) = struct.unpack("!HH", device_data[60:64])
                pkt_info = (pkt_num1, pkt_num2, step_count, checksum)
                payload = struct.unpack("!ffffffffffffff", device_data[4:60])
            return valid, pkt_info, payload
        except Exception as ex:
            s1 = device_data.encode("hex")
            print "Exception in parsing: " + ex.message + "\n, data="+s1
            # elif re.search(b'[\d|\w]+aa.*', s1):  # search and find new packet
            lst = re.findall(b'[\d|\w]+(aa.*)', s1)

            if lst:
                strrem = lst[0]
                lenght = len(strrem) / 2
                pktrem = device_data[-lenght:]
                newlen = PACKET_LEN - lenght
                device_data = self.read_device(newlen)
                device_data = pktrem + device_data
            else:
                device_data = self.read_device(PACKET_LEN)
            return self.parse_pkt(device_data)

    def create_ack(self, pkt_num1, pkt_num2):
        ack = []
        ack.append(1)
        ack.append(pkt_num1)
        ack.append(pkt_num2)
        ack.append((1 + pkt_num1 + pkt_num2) / 256)
        ack.append((1 + pkt_num1 + pkt_num2) % 256)
        # print "".join(str('{0:02x}'.format(e)) for e in ack)
        return "".join(str('{0:02x}'.format(e)) for e in ack).decode("hex")

    def calc_disp(self, sensor_data, theta):
        d0 = sensor_data[0]
        d1 = sensor_data[1]
        d2 = sensor_data[2]
        d3 = sensor_data[3]

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        dx = d0 * cos_theta - d1 * sin_theta
        dy = d0 * sin_theta + d1 * cos_theta
        dz = d2
        dp = d3

        disp = math.sqrt(dx * dx + dy * dy + dz * dz)
        return dx, dy, dz, dp, disp

    def calc_angle(self, x, y):
        if (y != 0) and (x != 0):
            angle = math.atan(x / y)
            angle = math.degrees(angle)
        else:
            if (x == 0):
                angle = 0
            else:
                angle = 90
        return angle

    def calc_dist(self, x, y, z):
        r = x * x + y * y + z * z
        return math.sqrt(r)

    def chk_ack(self, ack):
        # ack = read_device(4).encode("hex")
        # print "Received First acknowledgement ",ack.encode("hex")
        (start_code, state, chksum1, chksum2) = struct.unpack("!BBBB", ack[0:4])
        if start_code == 0xA0:
                return True
        else:
            s1 = ack.encode("hex")
            lst = re.findall(b'[\d|\w]+(a0.*)', s1)
            if lst:
                strrem = lst[0]
                lenght = len(strrem) / 2
                pktrem = ack[-lenght:]
                newlen = ACK_LEN - lenght
                ack = self.read_device(newlen)
                ack = pktrem + ack
            else:
                ack = self.read_device(ACK_LEN)
        return self.chk_ack(ack)

    def write_file_hdr(self):
        if os.path.exists(LOG_FILE) :
            created_time = datetime.datetime.fromtimestamp(os.path.getctime(LOG_FILE))
            backup_file = LOG_FILE + created_time.strftime("_%d%b%Y_%H%M")
            try:
                os.rename(LOG_FILE, backup_file)
            except WindowsError:
                os.remove(backup_file)
                os.rename(LOG_FILE, backup_file)

        self.outfile = open(LOG_FILE,"ab+")

        if self.outfile :
            str = "%10s\t%6s\t%6s\t%6s\t%6s\n" % ("PKT No.", "X", "Y", "Z", "Angle(Degree)")
            self.outfile.write(str)
            self.outfile.flush()

    def write_file(self, x, y, z,phi):
        dx = self.prev_x - x
        dy = self.prev_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        if (distance > 0.05):
            if self.outfile :
                str = "%d, %0.2f, %0.2f, %0.2f, %0.2f\n" % (self.pkt_counter, -x, y, -z, phi)
                self.outfile.write(str)
                self.outfile.flush()
                queue.put(str)
                self.prev_x = x
                self.prev_y = y
                self.pkt_counter += 1

    def IsDeviceActive(self):
        status = False
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.host, self.port))
            if result == 0:
                status = True
                # print "%s" % (self.host)
                # print sock.getsockname()
            else:
                status = False
            sock.close()
            # print remoteServerIP + " exit\n"
        except Exception as ex:
            status = False
        return status

    def reconnection(self):
        try:
            if self.client_socket :
                self.client_socket.close()
        except Exception as ex:
            print "Socket Closing Error ",str(ex)

        sys.stdout.write("Waiting for reconnection")
        while self.IsDeviceActive() == False:
            sys.stdout.write('.')
        sys.stdout.flush()
        print "."

        try:
            self.client_socket = self.open_device(self.host, self.port)
            self.client_socket.settimeout(TIME_OUT)
            print "Send last ack=", self.last_ack.encode("hex")

            self.write_device(self.last_ack)
            # self.sendStartCmd()
        except socket.error as ex:
            print "Reconnection: Exception on device connectivity " , str(ex.message)
            self.reconnection()

    def sendStartCmd(self):
        self.write_device(START_CMD.decode("hex"))
        try:
            ack = self.read_device(ACK_LEN)
        except DeviceConnectivityError as e:
            print "Exception on first ack : " + str(e)
            return
        self.chk_ack(ack)

    def run(self):
        # write command to start dead step reckoning
        try:
            self.client_socket = self.open_device(self.host, self.port)
            if self.client_socket:  # if btserial is not null:
                # global TIME_OUT
                print self.host, self.port, self.outfile
                self.write_file_hdr()
                cmd = START_CMD.decode("hex")
                self.write_device(cmd)
                print "Send Start Command: ", START_CMD
                self.client_socket.settimeout(TIME_OUT)
                count = 0
                num_pkts = 0
                curr_pkt = 0
                prev_pkt = -1
                xpos = 0.0  # x-coord in user's reference frame
                ypos = 0.0  # y-coord in user's reference frame
                zpos = 0.0  # z-coord in user's reference frame
                phi = 0.0  # Angular position around Z-axis in user's reference frame
                try:
                    ack = self.read_device(ACK_LEN)
                except DeviceConnectivityError as e:
                    print "Exception on first ack : "+str(e)
                    return
                self.chk_ack(ack)

                # while count < numbytes :
                last_ack = ''
                while g_isRunning:
                    try :
                        buffer = self.read_device(PACKET_LEN)
                        valid, packet_info, payload = self.parse_pkt(buffer)
                        # if not packet_info: break;

                        if (valid == False): continue

                        curr_pkt = packet_info[0] * 256 + packet_info[1]

                        if curr_pkt != prev_pkt:
                            # print "Read packet # %d...Sending Ack" % curr_pkt
                            dx, dy, dz, dp, disp = self.calc_disp(payload, phi)
                            xpos += dx
                            ypos += dy
                            zpos += dz
                            phi += dp
                            # radial_dist = self.calc_dist(xpos, ypos, zpos)  # for now do not factor in zpos
                            num_pkts += 1
                            count += PACKET_LEN
                            # print count
                            prev_pkt = curr_pkt
                            self.write_file(xpos, ypos, zpos, phi)

                        ack = self.create_ack(packet_info[0], packet_info[1])
                        self.last_ack = ack
                        self.write_device(ack)
                    except DeviceConnectivityError as ex:
                        print "Exception on device connectivity: "+str(ex.message)
                        self.reconnection()

            cmd = SYS_OFF_CMD.decode("hex")
            self.write_device(cmd)
            cmd = PROC_OFF_CMD.decode("hex")
            self.write_device(cmd)
            self.client_socket.close()
            self.outfile.close()
        except Exception as ex:
            # print "Exception: "+ str(ex.message)
            traceback.print_exc()
            if self.outfile :
                self.outfile.close()
        print "STOP"



# Create WriteToFile threads
try:
    thread.start_new_thread(monitorUserCmd, ( ))
    thread.start_new_thread(putDataToCloud, (queue, ))
except:
    print "Error: unable to start Monitor User's Cmd thread"



port = 9876
device_client = DeviceClient(device_ip, device_ip, port, queue)
device_client.start()
device_client.join()