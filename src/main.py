import signal
from datetime import datetime

import file_io
from classes import DirectoryNode, FS_Node, Memory
from menu import display_menu, exit_program, user_input

root: DirectoryNode = None
memory: Memory = None


def main():
    global root, memory

    root, memory = file_io.load_from_file()

    if not root or not memory:
        root = DirectoryNode('root', datetime.now())
        memory = Memory()

    FS_Node.set_memory(memory)

    display_menu()
    user_input(root, memory)


def handle_sigint(sig, frame):
    exit_program(root, memory)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_sigint)
    main()
