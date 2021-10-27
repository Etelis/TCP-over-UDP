import socket
import sys
import time

# Base variables and consts.
IP_ADDR = sys.argv[1]
PORT = int(sys.argv[2])
FILE_NAME = sys.argv[3]
DEFAULT_TIMEOUT = 12
FIN_MSG = b'FIN'
SYN_MSG = b'SYN'

# UDP socket initialisation
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(DEFAULT_TIMEOUT)
data_arr = [b'0']
ack_arr = [False]
arr_size_bytes = b'0'


# Variable initialization.
def initialize():
    global data_arr, ack_arr, arr_size_bytes
    text = open(FILE_NAME, "rb")
    data = text.read()
    # Make new array of bytes from current file, to each segment add 3-byte long sequence number.
    data_arr = [(data[i:i + 97] + int((i / 97)).to_bytes(3, 'little')) for i in range(0, len(data), 97)]
    arr_size_bytes = (len(data_arr)).to_bytes(3, 'little')
    # Make new boolean array to hold acknowledgments received.
    ack_arr = [False for i in range(0, len(data_arr), 1)]
    text.close()


# Sync method will be in charge of synchronizing connection with the server.
def syn():
    syn_msg = SYN_MSG + arr_size_bytes
    s.sendto(syn_msg, (IP_ADDR, PORT))
    # 2 ways handshake as the server is not communicating back but only receives data and approves it.
    try:
        get_syn, addr = s.recvfrom(100)
        if get_syn != syn_msg:
            syn()
        else:
            sent_pkgs()
    except socket.timeout:
        # in-case of drop re-send package.
        syn()


# will be in-charge of sending the packages that has not received ack yet.
def send_pkgs():
    for count, pkg in enumerate(data_arr):
        print("count = " + str(count))
        # Send only packages that has not received ack for.
        if not ack_arr[count]:
            s.sendto(pkg, (IP_ADDR, PORT))
            time.sleep(0.1)
    ack()


# will be in-charge of checking which acks have been received and marking the packages for future sending.
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
            send_pkgs()


# fin method will be in-charge to finish comunication with the server.
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
