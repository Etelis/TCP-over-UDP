import socket
import sys

# Base variables and consts.
PORT = int(sys.argv[1])
FIN_MSG = b'FIN'
SYN_MSG = b'SYN'
SYN_FLG = False
buffer_size = 0
MSS = 100


# UDP socket initialisation
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', PORT))


# THe following class will hold all server's information and will be in-charged of the data itself.
class ServerData:
    # Constructor - will initialize all variables needed.
    # @param buffer - the buffer size of files about to arrive.
    def __init__(self, buffer):
        # Make new array of bytes from current file, to each segment add 3-byte long sequence number.
        self.ack_array = [False] * buffer
        self.received_coutner = 0
        self.array_size = len(self.ack_array)
        self.data_arr = [b''] * buffer

    # receive ack - this method will be in-charged of receiving new package and inserting it into the data arr.
    def receive_ack(self, index, pkg_data):
        # if syn / fin ignore.
        if index < self.array_size:
            # if wasn't received before - mark package and add it to data arr.
            if not self.ack_array[index]:
                self.ack_array[index] = True
                self.data_arr[index] = pkg_data
                self.received_coutner += 1

    # get_printable_data - make a printable variable and return it for printing.
    def get_printable_data(self):
        printable_data = b''
        for pkg in self.data_arr:
            printable_data += pkg
        return printable_data.decode('utf-8')

    # is all received - check if all packages expected were added.
    def is_all_received(self):
        if self.received_coutner == self.array_size:
            return True
        return False


# function will receive packages and insert true to the boolean array if value was not received before.
def recv_pkg(pkg):
    pkg_num = int.from_bytes(pkg[-3:len(pkg)], 'little')
    pkg_data = pkg[0:len(pkg) - 3]
    s.sendto(pkg, client)
    server_data.receive_ack(pkg_num, pkg_data)


# syn function will resemble the sync method used by the TCP protocol to initialise the connection.
def syn(syn_msg, addr):
    s.sendto(syn_msg, addr)
    syn_msg, addr = s.recvfrom(MSS)
    # if the message received is not the first package, than resend the syn ack confirmation.
    if syn_msg == SYN_MSG:
        syn(syn_msg, client)
    else:
        return syn_msg


# This method will resemble the fin method used by the TCP protocol
# by the end of the connection will signal the server to stop.
def fin(finish_client):
    # timeout is set in-order to make sure no future messages are sent after fin
    s.settimeout(15)
    s.sendto(FIN_MSG, finish_client)
    try:
        fin_ack, finish_client = s.recvfrom(MSS)
        fin(finish_client)

    # if no message received within timeline move to initialize all variables.
    except socket.timeout:
        global SYN_FLG
        s.settimeout(None)
        SYN_FLG = False


# The following while loop will operate as the server itself, accepting connections and printing data.
while True:
    data, client = s.recvfrom(MSS)
    # if SYN_FLG off - meaning no sync was made with client yet, and message received is sync message,
    # synchronize connection.
    if not SYN_FLG and data[0:3] == SYN_MSG:
        # buffer_size is the amount of packages we are expecting.
        buffer_size = int.from_bytes(data[-3:len(data)], 'little')
        data = syn(data, client)
        SYN_FLG = True
        server_data = ServerData(buffer_size)
        recv_pkg(data)

    # if FIN message received after connection has been close
    # meaning the client did not receive the message and we should re send it
    else:
        fin(client)

    # if sync with client made successfully move to accept all packages from client.
    if SYN_FLG:
        # The next while loop will iterate until all packages received, meaning bool_arr is all true.
        while not server_data.is_all_received():
            data, client = s.recvfrom(MSS)
            recv_pkg(data)
        # all packages has been successfully accepted, we will print the data and finnish connection with client.
        print(server_data.get_printable_data())
        fin(client)
