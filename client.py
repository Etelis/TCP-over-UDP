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


class Data:
    def __init__(self, file_name):
        data = open(file_name, "rb").read()
        # Make new array of bytes from current file, to each segment add 3-byte long sequence number.
        self.data_arr = [(data[i:i + 97] + int((i / 97)).to_bytes(3, 'little')) for i in range(0, len(data), 97)]
        # Make new boolean array to hold acknowledgments received.
        self.ack_arr = [False] * len(self.data_arr)
        self.arr_size_bytes = (len(self.data_arr)).to_bytes(3, 'little')

    def is_acked(self, n):
        return self.ack_arr[n]

    def notify_ack(self, index):
        self.ack_arr[index] = True

    def get_size(self):
        return self.arr_size_bytes

    def get_data_arr(self):
        return self.data_arr

    def done_acking(self):
        for ack in self.ack_arr:
            if not ack:
                return False
        return True


# UDP socket initialisation
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(DEFAULT_TIMEOUT)


# Sync method will be in charge of synchronizing connection with the server.
def syn():
    syn_msg = SYN_MSG + data_toSend.get_size()
    s.sendto(syn_msg, (IP_ADDR, PORT))
    # 2 ways handshake as the server is not communicating back but only receives data and approves it.
    try:
        get_syn, addr = s.recvfrom(100)
        if get_syn != syn_msg:
            syn()
        else:
            send_pkgs()
    except socket.timeout:
        # in-case of drop re-send package.
        syn()


# will be in-charge of sending the packages that has not received ack yet.
def send_pkgs():
    for count, pkg in enumerate(data_toSend.get_data_arr()):
        print("count = " + str(count))
        # Send only packages that has not received ack for.
        if not data_toSend.is_acked(count):
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
            data_toSend.notify_ack(pkg_num)

    except socket.timeout:
        if not data_toSend.done_acking():
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


data_toSend = Data(FILE_NAME)
syn()
