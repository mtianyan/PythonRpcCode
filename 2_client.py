# coding: utf-8
# client

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 8080))  # 连接服务器
sock.sendall(b"hello")  # 将消息输出到发送缓冲 send buffer
print(sock.recv(1024))  # 从接收缓冲 recv buffer 中读响应
sock.close() # 关闭套接字