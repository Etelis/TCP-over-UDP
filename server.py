import socket
import sys

port = int(sys.argv[1])
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind('', port)

num_pak, addr = s.recvfrom(3)
s.sendto(num_pak, addr)
num_pak_int = int.from_bytes(num_pak, 'little')
arr_data = [b'0'] * num_pak_int
arr_bool = [False for i in range(num_pak_int)]
count = 0
while count != num_pak_int:
    data, addr = s.recvfrom(100)
    if data == num_pak:
        s.sendto(num_pak, addr)
    else:
        pkn_num = int.from_bytes(data[-3:len(data)], 'little')
        print(pkn_num)
        if not arr_bool[pkn_num]:
            arr_data[pkn_num] = data
            arr_bool[pkn_num] = True
            count += 1
        s.sendto(data, addr)

for chunk in arr_data:
    print(chunk.decode('utf8'))

s.close()
