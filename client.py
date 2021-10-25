import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b'Ben Levi 318811304', ('192.168.129.128', 12345))

data, addr = s.recvfrom(1024)
print(str(data), addr)

s.close()
