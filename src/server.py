import signal
import socket
import sys
from _thread import allocate_lock, start_new_thread
from datetime import datetime
from io import StringIO
from client import BUFFER_SIZE

import file_io
from classes import DirectoryNode, FS_Node, Memory
from menu import display_menu, exit_program, execute_command

root: DirectoryNode = None
memory: Memory = None

HOST = "127.0.0.1"
PORT = 95

BUFFER_SIZE = 1024


def main():
    global root, memory

    root, memory = file_io.load_from_file()

    if not root or not memory:
        root = DirectoryNode('/', datetime.now())
        memory = Memory()

    FS_Node.memory = memory

    start_server(HOST, PORT)


def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        print(f"Server started at {host}:{port}...")

        while True:
            accept_connections(s)


def accept_connections(serverSocket):
    client, addr = serverSocket.accept()
    write_lock = allocate_lock()
    start_new_thread(client_handler, (client, addr, write_lock))


def client_handler(conn, addr, write_lock):
    with conn:
        user = conn.recv(BUFFER_SIZE).decode()
        print(F'Connected by {user} at {addr[0]}:{addr[1]}')

        buffer = StringIO()
        sys.stdout = buffer
        display_menu()
        sys.stdout = sys.__stdout__
        conn.sendall(buffer.getvalue().encode())

        cwd = root

        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            # print the data received from the client
            print(f"Received from {user}:  {data}")

            if data.decode().startswith('exit'):
                break

            buffer.truncate(0)
            sys.stdout = buffer
            cwd = execute_command(conn, root, memory,
                                  data.decode(), write_lock, cwd)
            sys.stdout = sys.__stdout__
            data = buffer.getvalue()
            print('-->', data)
            conn.sendall(data.encode())


def handle_sigint(sig, frame):
    exit_program(root, memory)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_sigint)
    main()
