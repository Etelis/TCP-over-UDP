import socket
import sys
import time

ip = sys.argv[1]
port = sys.argv[2]
file_name = sys.argv[3]

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(12)

with open(file_name) as file :
    data = file.read()
    arr = [data[i:i + 96] for i in range(0, len(data), 96)]
    for i in range(0, len(arr)):
        if (i < 10):
            arr[i] += '00' + str(i)
        elif (i < 100):
            arr[i] += '0' + str(i)
        else:
            arr[i] += str(i)

ack_arr =  [False for i in range(len(arr))]

def start_net(num_pak):
    s.sendto(bytes(num_pak), (ip, port))
    try:
        data, addr = s.recvfrom(3)
        send_paks()
    except socket.timeout:
        start_net(num_pak)

def send_paks():
    count = 0
    for pak in arr:
        if ack_arr[count] == False:
            s.sendto(bytes(pak), (ip, port))
            time.sleep(0.1)
        count += 1
    ack()

def ack():
    try:
        while True:
            data, addr = s.recvfrom(100)
            pck_num = str(data)[-3:len(str(data))]
            ack_arr[int(pck_num)] = True
    except:
        if not finish():
            send_paks()

def finish():
    for b in ack_arr:
        if not b:
            return False
    return True


start_net(len(arr))
s.close()
