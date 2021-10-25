import socket
import sys
import time

ip = sys.argv[1]
port = int(sys.argv[2])
file_name = sys.argv[3]

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(12)

text = open(file_name, "rb")
data = text.read()
arr = [data[i:i + 97] for i in range(0, len(data), 97)]
for i in range(0, len(arr)):
    arr[i] += i.to_bytes(3, 'little')

ack_arr = [False for i in range(len(arr))]


def start_net(num_pak):
    s.sendto(num_pak, (ip, port))
    try:
        get_num, addr = s.recvfrom(3)
        send_paks()
    except socket.timeout:
        start_net(num_pak)


def send_paks():
    count = 0
    for pak in arr:
        if not ack_arr[count]:
            s.sendto(pak, (ip, port))
            time.sleep(0.1)
        count += 1
    ack()


def ack():
    try:
        while True:
            data_ack, addr = s.recvfrom(100)
            pck_num = int.from_bytes(data_ack[-3:len(data_ack)], 'little')
            ack_arr[pck_num] = True
    except:
        if not finish():
            send_paks()


def finish():
    for b in ack_arr:
        if not b:
            return False
    return True


start_net((len(arr)).to_bytes(3, 'little'))
s.close()
