from datetime import datetime
from classes import DirectoryNode, Memory
import file_io
import signal
from menu import display_menu, user_input, exit_program


root: DirectoryNode = None
memory: Memory = None


def main():
    global root, memory

    root, memory = file_io.load_from_file()

    if not root or not memory:
        root = DirectoryNode('root', datetime.now())
        memory = Memory()

    signal.signal(signal.SIGINT, handle_sigint)

    display_menu()
    user_input(root, memory)


def handle_sigint(sig, frame):
    exit_program(root, memory)


if __name__ == '__main__':
    main()
