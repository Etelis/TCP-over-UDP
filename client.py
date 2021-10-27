import socket
import sys
import time

IP_ADDR = sys.argv[1]
PORT = int(sys.argv[2])
FILE_NAME = sys.argv[3]
DEFAULT_TIMEOUT = 12
FIN_MSG = b'FIN'
SYN_MSG = b'SYN'


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(DEFAULT_TIMEOUT)
data_arr = [b'0']
ack_arr = [False]
arr_size_bytes = b'0'


def initialize():
    global data_arr, ack_arr, arr_size_bytes
    text = open(FILE_NAME, "rb")
    data = text.read()
    data_arr = [(data[i:i + 97] + int((i / 97)).to_bytes(3, 'little')) for i in range(0, len(data), 97)]
    arr_size_bytes = (len(data_arr)).to_bytes(3, 'little')
    ack_arr = [False for i in range(0, len(data_arr), 1)]
    text.close()


def syn():
    syn_msg = SYN_MSG + arr_size_bytes
    s.sendto(syn_msg, (IP_ADDR, PORT))
    try:
        get_syn, addr = s.recvfrom(100)
        if get_syn != syn_msg:
            syn()
        else:
            sent_pkgs()
    except socket.timeout:
        syn()


def sent_pkgs():
    count = 0
    for count, pkg in enumerate(data_arr):
        print("count = " + str(count))
        if not ack_arr[count]:
            s.sendto(pkg, (IP_ADDR, PORT))
            time.sleep(0.1)
    ack()


def ack():
    try:
        while True:
            data_ack, addr = s.recvfrom(100)
            if data_ack == FIN_MSG:
                fin()
            pkg_num = int.from_bytes(data_ack[-3:len(data_ack)], 'little')
            print("got ack for:" + str(pkg_num))
            ack_arr[pkg_num] = True

    except socket.timeout:
        if not finish():
            sent_pkgs()


def fin():
    try:
        print("Waiting for server to return ack")
        s.sendto(FIN_MSG, (IP_ADDR, PORT))
        fin_ack, addr = s.recvfrom(100)
        if fin_ack != FIN_MSG:
            fin()
        else:
            print("Received bye bye!")
            s.close()
            sys.exit()
    except socket.timeout:
        fin()


def finish():
    for b in ack_arr:
        if not b:
            return False
    return True


initialize()
syn()
