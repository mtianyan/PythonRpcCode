# coding: utf
# sendmsg recvmsg python3.5+才可以支持

import os
import json
import struct
import socket


def handle_conn(conn, addr, handlers):
    print(addr, "comes")
    while True:
        # 简单起见，这里就没有使用循环读取了
        length_prefix = conn.recv(4)
        if not length_prefix:
            print(addr, "bye")
            conn.close()
            break  # 关闭连接，继续处理下一个连接
        length, = struct.unpack("I", length_prefix)
        body = conn.recv(length)
        request = json.loads(body)
        in_ = request['in']
        params = request['params']
        print(in_, params)
        handler = handlers[in_]
        handler(conn, params)


def loop_slave(pr, handlers):
    while True:
        bufsize = 1
        ancsize = socket.CMSG_LEN(struct.calcsize('i'))
        msg, ancdata, flags, addr = pr.recvmsg(bufsize, ancsize)
        cmsg_level, cmsg_type, cmsg_data = ancdata[0]
        fd = struct.unpack('i', cmsg_data)[0]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno=fd)
        handle_conn(sock, sock.getpeername(), handlers)


def ping(conn, params):
    send_result(conn, "pong", params)


def send_result(conn, out, result):
    response = json.dumps({"out": out, "result": result}).encode('utf-8')
    length_prefix = struct.pack("I", len(response))
    conn.sendall(length_prefix)
    conn.sendall(response)


def loop_master(serv_sock, pws):
    idx = 0
    while True:
        sock, addr = serv_sock.accept()
        pw = pws[idx % len(pws)]
        # 消息数据，whatever
        msg = [b'x']
        # 辅助数据，携带描述符
        ancdata = [(
            socket.SOL_SOCKET,
            socket.SCM_RIGHTS,
            struct.pack('i', sock.fileno()))]
        pw.sendmsg(msg, ancdata)
        sock.close()  # 关闭引用
        idx += 1


def prefork(serv_sock, n):
    pws = []
    for i in range(n):
        # 开辟父子进程通信「管道」
        pr, pw = socket.socketpair()
        pid = os.fork()
        if pid < 0:  # fork error
            return pws
        if pid > 0:
            # 父进程
            pr.close()  # 父进程不用读
            pws.append(pw)
            continue
        if pid == 0:
            # 子进程
            serv_sock.close()  # 关闭引用
            pw.close()  # 子进程不用写
            return pr
    return pws


if __name__ == '__main__':
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sock.bind(("localhost", 8080))
    serv_sock.listen(1)
    pws_or_pr = prefork(serv_sock, 10)
    if hasattr(pws_or_pr, '__len__'):
        if pws_or_pr:
            loop_master(serv_sock, pws_or_pr)
        else:
            # fork 全部失败，没有子进程，Game Over
            serv_sock.close()
    else:
        handlers = {
            "ping": ping
        }
        loop_slave(pws_or_pr, handlers)