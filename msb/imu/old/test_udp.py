import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("192.168.1.3", 6666))

while True:
    d = s.recvfrom(1024)
    print(f'received: {d}')