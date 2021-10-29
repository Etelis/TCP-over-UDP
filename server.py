import socket
import sys

# Base variables and consts.
PORT = int(sys.argv[1])
FIN_MSG = b'FIN'
SYN_MSG = b'SYN'
SYN_FLG = False
buffer_size = 0
bool_arr = [False]
data_arr = []
iteration_counter = 1

# UDP socket initialisation
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', PORT))


# function will receive packages and insert true to the boolean array if value was not received before.
def recv_pkg(pkg):
    pkg_num = int.from_bytes(pkg[-3:len(pkg)], 'little')
    s.sendto(pkg, client)
    if not bool_arr[pkg_num]:
        print("Got package: " + str(pkg_num))
        data_arr[pkg_num] = data
        bool_arr[pkg_num] = True
        return 1
    return 0


# syn function will resemble the sync method used by the TCP protocol to initialise the connection.
def syn(syn_msg, addr):
    s.sendto(syn_msg, addr)
    syn_msg, addr = s.recvfrom(100)
    # if the message received is not the first package, than resend the syn ack confirmation.
    if (int.from_bytes(syn_msg[-3:len(syn_msg)], 'little')) != 0:
        print("Wanted pkg 000, but got: " + str(int.from_bytes(syn_msg[-3:len(syn_msg)], 'little')))
        syn(syn_msg, client)
    # otherwise, return the 000 package and move on to accepting packages.
    else:
        return syn_msg


# This function will print the data when all received.
def print_data():
    print("Printing stage")
    for chunk in data_arr:
        print(chunk.decode('utf8'))


# This function will initialize all variables before each socket connected.
def initialize():
    print("Finished And initialized.")
    global buffer_size, bool_arr, data_arr, SYN_FLG, iteration_counter
    buffer_size = 0
    bool_arr = [False]
    data_arr = [b'0']
    SYN_FLG = False
    iteration_counter = 1
    s.settimeout(None)


# This method will resemble the fin method used by the TCP protocol
# by the end of the connection will signal the server to stop.
def fin(client):
    # timeout is set in-order to make sure no future messages are sent after fin
    s.settimeout(15)
    s.sendto(FIN_MSG, client)
    try:
        fin_ack, client = s.recvfrom(100)
        fin(client)

    # if no message received within timeline move to initialize all variables.
    except socket.timeout:
        initialize()


# The following while loop will operate as the server itself, accepting connections and printing data.
while True:
    data, client = s.recvfrom(100)
    # if SYN_FLG off - meaning no sync was made with client yet, and message received is sync message,
    # synchronize connection.
    if not SYN_FLG and data[0:3] == SYN_MSG:
        # buffer_size is the amount of packages we are expecting.
        buffer_size = int.from_bytes(data[-3:len(data)], 'little')
        data = syn(data, client)
        print("Buffer size is:" + str(buffer_size))
        SYN_FLG = True
        # Initialize arrays according to size received.
        bool_arr = [False for i in range(0, buffer_size, 1)]
        data_arr = [b'0'] * buffer_size
        recv_pkg(data)

    # if FIN message received after connection has been close
    # meaning the client did not receive the message and we should re send it
    else:
        fin(client)

    # if sync with client made successfully move to accept all packages from client.
    if buffer_size > 0:
        # The next while loop will iterate until all packages received, meaning bool_arr is all true.
        while iteration_counter < buffer_size:
            data, client = s.recvfrom(100)
            print("iteration_counter = " + str(iteration_counter))
            # if package received was not received before rev_pkg will return 1, otherwise expect 0.
            iteration_counter += recv_pkg(data)
        # all packages has been successfully accepted, we will print the data and finnish connection with client.
        print_data()
        fin(client)
