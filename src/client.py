# echo-client.py

import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65430  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # take user input until 'exit' is entered
    while True:
        data = s.recv(1024*4)
        print(f"Received: \n{data.decode()}")
        data = input("Enter data to send to server: ")
        s.sendall(data.encode())
        if data == "exit":
            break
