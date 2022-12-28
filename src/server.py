import signal
from datetime import datetime
import socket
import sys
from io import StringIO
from _thread import *

import file_io
from classes import DirectoryNode, FS_Node, Memory
from menu import display_menu, exit_program, user_input

root: DirectoryNode = None
memory: Memory = None

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
# Port to listen on (non-privileged ports are > 1023)memory: Memory = None
PORT = 65430


def client_handler(conn, addr):
    with conn:
        user = conn.recv(1024).decode()
        print(F'Connected by {user} at {addr[0]}:{addr[1]}')

        buffer = StringIO()
        sys.stdout = buffer
        display_menu()
        sys.stdout = sys.__stdout__
        conn.sendall(buffer.getvalue().encode())

        while True:
            data = conn.recv(1024)
            if not data:
                break
            # print the data received from the client
            print(f"Received from {user}:  {data}")

            buffer.truncate(0)
            sys.stdout = buffer
            user_input(root, memory, data.decode())
            sys.stdout = sys.__stdout__
            data = buffer.getvalue()
            print('-->', data)
            conn.sendall(data.encode())


def accept_connections(serverSocket):
    client, addr = serverSocket.accept()
    start_new_thread(client_handler, (client, addr))


def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        while True:
            accept_connections(s)


def main():
    global root, memory

    root, memory = file_io.load_from_file()

    if not root or not memory:
        root = DirectoryNode('/', datetime.now())
        memory = Memory()

    FS_Node.memory = memory

    start_server(HOST, PORT)


def handle_sigint(sig, frame):
    exit_program(root, memory)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_sigint)
    main()
