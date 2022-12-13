import signal
import sys
from datetime import datetime

import file_io
from classes import DirectoryNode, FS_Node, Memory
from menu import execute_command, exit_program
import threading

root: DirectoryNode = None
memory: Memory = None

INPUT_FILENAME_PREFIX = 'input_thread'
OUTPUT_FILENAME_PREFIX = 'output_thread'


def main():
    global root, memory

    root, memory = file_io.load_from_file()

    if not root or not memory:
        root = DirectoryNode('/', datetime.now())
        memory = Memory()

    FS_Node.memory = memory

    if len(sys.argv) != 2:
        print('Usage: python3 main.py <number of threads>')
        return

    num_threads = int(sys.argv[1])

    threads = []
    for thread_id in range(num_threads):
        threads.append(threading.Thread(
            target=thread_worker,
            args=(thread_id + 1, INPUT_FILENAME_PREFIX, OUTPUT_FILENAME_PREFIX)
        ))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print('All threads finished')


def thread_worker(thread_id, input_filename_prefix, output_filename_prefix):
    print(f'Thread {thread_id} started')

    with open(f"{input_filename_prefix}{thread_id}.txt", 'r') as input_file:
        with open(f"{output_filename_prefix}{thread_id}.txt", 'w') as output_file:
            for line in input_file:
                command = line.strip()
                execute_command(command, output_file, root, memory)

    print(f'Thread {thread_id} finished')


def handle_sigint(sig, frame):
    exit_program(root, memory)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_sigint)
    main()
