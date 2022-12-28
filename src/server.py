import signal
from datetime import datetime
import socket
import sys
from io import StringIO

import file_io
from classes import DirectoryNode, FS_Node, Memory
from menu import display_menu, exit_program, user_input

root: DirectoryNode = None
memory: Memory = None

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
# Port to listen on (non-privileged ports are > 1023)memory: Memory = None
PORT = 65430


def main():
    global root, memory

    root, memory = file_io.load_from_file()

    if not root or not memory:
        root = DirectoryNode('/', datetime.now())
        memory = Memory()

    FS_Node.memory = memory
    buffer = StringIO()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            sys.stdout = buffer
            display_menu()
            sys.stdout = sys.__stdout__
            conn.sendall(buffer.getvalue().encode())

            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # print the data received from the client
                print(f"Received: \n{data!r}")

                buffer.truncate(0)
                sys.stdout = buffer
                user_input(root, memory, data.decode())
                sys.stdout = sys.__stdout__
                data = buffer.getvalue()
                print('-->', data)
                conn.sendall(data.encode())


def handle_sigint(sig, frame):
    exit_program(root, memory)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_sigint)
    main()
