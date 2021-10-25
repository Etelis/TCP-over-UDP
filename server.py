import socket
import sys

port = sys.argv[1]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', int(port)))
num_pak, addr = s.recvfrom(3)
s.sendto(num_pak, addr)
arr_data = ['0'] * int((num_pak).decode('utf8'))
arr_bool = [False for i in range(int(num_pak))]
count = 0
print("check")
while count != int(num_pak):
    data, addr = s.recvfrom(100)
    if data == num_pak:
        s.sendto(num_pak, addr)
    else:
        pkn_num = str(data)[-3:len(str(data))]
        if not arr_bool[int(pkn_num)]:
            arr_data[int(pkn_num)] = str(data)
            arr_bool[int(pkn_num)] = True
            count += 1
        s.sendto(data, addr)

for chunk in arr_data:
    print(chunk)