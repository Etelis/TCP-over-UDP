import socket
import sys
import time

# Base variables and consts.
IP_ADDR = sys.argv[2]
PORT = int(sys.argv[1])
FILE_NAME = sys.argv[3]
DEFAULT_TIMEOUT = 5
MSS = 97
ADDR = (IP_ADDR, PORT)
NULL = b'0'
FIN_MSG = b'FIN'
SYN_MSG = b'SYN'
MAX_PORT = 65535


# Data Class - will hold all information of packages needed to be sent and ack received.
class Data:
    # Constructor - initialize variables and split file into small chunks.
    def __init__(self, file_name):
        try:
            data = open(file_name, "rb").read()
        except OSError:
            print("Cannot open or read file")
            s.close()
            sys.exit()
        # Make new array of bytes from current file, to each segment add 3-byte long sequence number.
        self.data_arr = [(data[i:i + MSS] + int((i / MSS)).to_bytes(3, 'little')) for i in range(0, len(data), MSS)]
        # Size of the array.
        self.arr_size_bytes = (len(self.data_arr)).to_bytes(3, 'little')
        # Counter to hold the amount of packages received.
        self.received_coutner = 0

    # Iterator made for giving the next package in line that did not received ack for.
    def __iter__(self):
        self.iter = 0
        return self

    def __next__(self):
        # While we didn't reach the end of the array look for a package that have not received ack for.
        while self.iter < len(self.data_arr):
            # if found return it.
            if self.data_arr[self.iter] != NULL:
                temp = self.iter
                self.iter += 1
                return self.data_arr[temp]
            self.iter += 1
        raise StopIteration

    # notify_ack - Method will update the current list for the ack received, if new ack will increase received_counter.
    def notify_ack(self, index):
        if self.data_arr[index] != NULL:
            self.data_arr[index] = NULL
            self.received_coutner += 1

    # get_size - as simple as it gets, returns size.
    def get_size(self):
        return self.arr_size_bytes

    # done_acking - returns true if all acks has been received, otherwise false.
    def done_acking(self):
        if self.received_coutner == len(self.data_arr):
            return True
        return False


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
    for pkg in data_toSend:
        s.sendto(pkg, ADDR)
    mark_acks()


# will be in-charge of checking which acks have been received and marking the packages for future sending.
def mark_acks():
    try:
        # while still un-resolved packages in buffer keep marking them.
        while True:
            data_ack, address = s.recvfrom(100)
            # if message is fin message go to fin and finish the connection.
            if data_ack == FIN_MSG:
                fin()
            # if syn message was found again meaning sever did not receive last one, client will resend it.
            if data_ack == SYN_MSG:
                syn()
            # otherwise store the ack received and mark the pacakge.
            pkg_num = int.from_bytes(data_ack[-3:len(data_ack)], 'little')
            data_toSend.notify_ack(pkg_num)

    except socket.timeout:
        if not data_toSend.done_acking():
            send_pkgs()


# fin method will be in-charge to finish comunication with the server.
def fin():
    try:
        s.sendto(FIN_MSG, (IP_ADDR, PORT))
        fin_ack, address = s.recvfrom(100)
        if fin_ack != FIN_MSG:
            fin()
        else:
            s.close()
            sys.exit()
    except socket.timeout:
        fin()


# validates IP address's format
def validate_ip():
    ip_parts = IP_ADDR.split(".")

    if len(ip_parts) != 4:
        return False

    for part in ip_parts:
        if not isinstance(int(part), int):
            return False

        if int(part) < 0 or int(part) > 255:
            return False

    return True


# checks arguments before staring.
def args_check():
    try:
        if MAX_PORT < int(PORT) or int(PORT) < 0:
            raise "Port is not in the correct range"

        if len(sys.argv) != 4:
            raise "Wrong amount of arguments."

        if not validate_ip():
            raise "Wrong IP address format."

    except:
        s.close()
        sys.exit()


# UDP socket initialisation
args_check()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(DEFAULT_TIMEOUT)

data_toSend = Data(FILE_NAME)
syn()
