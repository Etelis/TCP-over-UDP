import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 12345))

while True:
    data, addr = s.recvfrom(1024)
    print(str(data), addr)
    s.sendto(data.upper(), addr)
