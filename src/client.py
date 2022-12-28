import socket

HOST = "127.0.0.1"
PORT = 95

BUFFER_SIZE = 1024 * 16


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            print("Connection refused. Server unavailable.")
            return

        # take username and send to server
        username = input("Enter username: ")
        s.sendall(username.encode())

        # take user input until 'exit' is entered
        while True:
            data = s.recv(BUFFER_SIZE)
            print(f"Received: \n{data.decode()}")
            data = input("Enter data to send to server: ")
            s.sendall(data.encode())
            if data == "exit":
                break


if __name__ == "__main__":
    main()
