# coding: utf-8
# server

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("localhost", 8080))
sock.listen(1)  # 监听客户端连接
while True:
    conn, addr = sock.accept()  # 接收一个客户端连接
    print(conn.recv(1024))  # 从接收缓冲读消息 recv buffer
    conn.sendall(b"world")  # 将响应发送到发送缓冲 send buffer
    conn.close() # 关闭连接