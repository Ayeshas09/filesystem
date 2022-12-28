from socket import socket
import time
from datetime import datetime
from typing import List

import file_io
from classes import DirectoryNode, FS_Node, FileNode, Memory
from utils import bytes_to_string, split_strip, string_to_bytes

menu = {
    'help': 'Display this menu',

    'touch <filename>': 'Create a new file',
    'rm <filename | dirname>': 'Remove a file',
    'mkdir <dirname>': 'Create a new directory',
    'cd <path>': 'Change directory',
    'mv <in filename | dirname> <out filename | dirname>': 'Move a file or directory',

    'open <filename> <mode (r, w, a )>': 'Open a file',
    'wf <filename> <content>': 'Write to a file',
    'af <filename> <content>': 'Append to a file',
    'mwf <filename> <starting byte> <content length> <writing byte>': 'Move content within a file',
    'close <filename>': 'Close a file',

    'cat <filename>': 'Read from a file',
    'rf <filename> <starting byte> <content length>': 'Read from a file from a specific byte',

    'mmap': 'Display memory map',

    'ls <path>': 'List files and directories',
    'exit': 'Exit the program'
}


def display_menu():
    print('---------- Available Commands ----------')
    for key, value in menu.items():
        print(f'-- {key}  :  {value}')

    print('----------------------------------------')


def init_exchange(root: DirectoryNode, memory: Memory, conn: socket):
    # Returns an identifier for the connection
    return {
        "root": root,
        "cwd": root,
        "memory": memory,
        "id": conn,
    }


def user_input(root: DirectoryNode, cwd: DirectoryNode, memory: Memory, id: socket, command: str):
    currentDir = cwd

    command = command.strip()

    if command == 'help':
        display_menu()

    elif command.startswith('exit'):
        exit_program(root, memory)

    elif command.startswith('touch'):
        _, filename = split_strip(command, ' ')
        touch(currentDir, filename)

    elif command.startswith('mkdir'):
        _, dirname = split_strip(command, ' ')
        mkdir(currentDir, dirname)

    elif command.startswith('ls'):
        if command == 'ls':
            currentDir.print_directory_structure()

        else:
            _, path = command.split(' ')
            ls(currentDir, path)

    elif command.startswith('rm'):
        _, name = split_strip(command, ' ')
        remove(currentDir, name)

    elif command.startswith('mv'):
        _, name, destination = split_strip(command, ' ')
        move(currentDir, name, destination)

    elif command.startswith('cd'):
        _, path = split_strip(command, ' ')

        currentDir = change_dir(currentDir, path)

    elif command.startswith('wf'):
        segments = split_strip(command, ' ')
        filename = segments[1]
        content = ' '.join(segments[2:])

        write_file(currentDir, filename, content)

    elif command.startswith('af'):
        segments = split_strip(command, ' ')
        filename = segments[1]
        content = ' '.join(segments[2:])

        append_file(currentDir, filename, content)

    elif command.startswith('mwf'):
        segments = split_strip(command, ' ')
        filename = segments[1]
        starting_byte = int(segments[2])
        content_length = int(segments[3])
        writing_byte = int(segments[4])

        move_within_file(currentDir, filename, starting_byte,
                         content_length, writing_byte)

    elif command.startswith('cat'):
        _, filename = split_strip(command, ' ')

        display_file(currentDir, filename)

    elif command.startswith('rf'):
        segments = split_strip(command, ' ')
        filename = segments[1]
        starting_byte = int(segments[2])
        content_length = int(segments[3])

        display_file(currentDir, filename, starting_byte, content_length)

    elif command.startswith('open'):
        segments = split_strip(command, ' ')
        filename = segments[1]
        mode = segments[2]

        open_file(currentDir, filename, mode)

    elif command.startswith('close'):
        _, filename = split_strip(command, ' ')

        close_file(currentDir, filename)

    elif command.startswith('mmap'):
        memory.show_memory_map()
        memory.show_memory_layout()

    else:
        print('Invalid command!')


def touch(currentDir, name: str):
    if currentDir.get_child(name):
        print('File already exists!')

    else:
        new_file = currentDir.add_child(FileNode(name, datetime.now()))
        print('File has been created successfully!')
        return new_file


def remove(currentDir, name):
    if currentDir.get_child(name):
        child = currentDir.get_child(name)
        currentDir.remove_child(child)
        print('Deleted successfully!')

    else:
        print('No such file or directory exists!')


def mkdir(currentDir, name: str):
    if currentDir.get_child(name):
        print('Directory already exists!')

    else:
        new_dir = currentDir.add_child(DirectoryNode(name, datetime.now()))
        print('Directory has been created successfully!')
        return new_dir


def ls(currentDir, path):
    if path == '..':
        if currentDir.parent:
            currentDir.parent.print_directory_structure()
        else:
            print('No such path exists!')

    else:
        if currentDir.get_child(path):
            currentDir.get_child(path).print_directory_structure()
        else:
            print('No such path exists!')


def move(currentDir, name, new_name):
    if currentDir.get_child(name):
        child = currentDir.get_child(name)

        if '/' in new_name:
            dir, file = new_name.split('/')
            new_dir = currentDir.get_child(dir)
            currentDir.remove_child(child)
            new_dir.add_child(child)

            if currentDir.get_child(file):
                old_file = currentDir.get_child(file)
                currentDir.remove_child(old_file)
                del old_file

            child.name = file

        else:

            if isinstance(currentDir.get_child(new_name), DirectoryNode):
                new_dir = currentDir.get_child(new_name)
                currentDir.remove_child(child)
                new_dir.add_child(child)

            else:
                if currentDir.get_child(new_name):
                    old_file = currentDir.get_child(new_name)
                    currentDir.remove_child(old_file)
                    del old_file

                child.name = new_name

        print('Moved successfully!')

    else:
        print('No such file or directory exists!')


def change_dir(currentDir, path):
    if path == '..':
        return currentDir.parent if currentDir.parent else currentDir

    elif currentDir.get_child(path):
        return currentDir.get_child(path)

    print("No such directory exists")
    return currentDir


def write_file(currentDir: DirectoryNode, filename: str, content: List[str]):
    memory = FS_Node.memory

    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!')
        return

    if file.state == FileNode.STATE_OPEN and file.mode == FileNode.MODE_WRITE:
        content_bytes = string_to_bytes(content)
        if file.starting_addr < 0 and file.size == 0:
            try:
                file.starting_addr = memory.allocate(len(content_bytes))
                file.size = len(content)
            except ValueError:
                print('Not enough memory!')
                return

        file.starting_addr = memory.write_file(
            file.starting_addr, content_bytes)

        file.date_modified = datetime.now()
        print('File written successfully!')

    else:
        print('File is not open in write mode!')


def append_file(currentDir: DirectoryNode, filename: str, new_content: List[str]):
    memory = FS_Node.memory
    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!')
        return

    if file.state == FileNode.STATE_OPEN and file.mode == FileNode.MODE_APPEND:
        new_content_bytes = string_to_bytes(new_content)
        if file.starting_addr < 0 and file.size == 0:
            try:
                file.starting_addr = memory.allocate(len(new_content_bytes))
            except ValueError:
                print('Not enough memory!')
                return

        file.starting_addr = memory.append_file(
            file.starting_addr, new_content_bytes)

        file.size += len(new_content)
        file.date_modified = datetime.now()
        print('File appended successfully!')

    else:
        print('File is not open in append mode!')


def move_within_file(currentDir: DirectoryNode, filename: str, starting_byte: int, content_length: int, writing_byte: int):
    memory = FS_Node.memory
    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!')
        return

    if file.state == FileNode.STATE_OPEN and file.mode == FileNode.MODE_WRITE:
        if file.starting_addr < 0 and file.size == 0:
            print('File is empty!')
            return

        if starting_byte + content_length > file.size:
            print('Invalid starting byte and content length!')
            return

        if writing_byte > file.size:
            print('Invalid writing byte!')
            return

        file.starting_addr = memory.move_within_file(
            file.starting_addr, starting_byte, content_length, writing_byte)

        file.date_modified = datetime.now()
        print('File moved successfully!')


def display_file(currentDir: DirectoryNode, filename: str, starting_byte: int = 0, content_length: int = -1):
    memory = FS_Node.memory
    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!')
        return

    if file.state == FileNode.STATE_OPEN and file.mode == FileNode.MODE_WRITE:
        if file.starting_addr < 0 and file.size == 0:
            print()
            return

        content = bytes_to_string(
            memory.read_file(
                file.starting_addr,
                starting_byte=starting_byte,
                num_bytes=file.size if content_length == -1 else content_length)
        )

        print(content)

    else:
        print('File is not open in read mode!')


def open_file(currentDir: DirectoryNode, filename: str, mode: str):
    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!')
        return

    if mode in [FileNode.MODE_NONE, FileNode.MODE_READ, FileNode.MODE_WRITE, FileNode.MODE_APPEND]:
        file.mode = mode
        file.state = FileNode.STATE_OPEN
        print('File opened successfully!')
    else:
        print('Invalid mode!')


def close_file(currentDir: DirectoryNode, filename: str):
    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!')
        return

    if file.state == FileNode.STATE_OPEN:
        file.state = FileNode.STATE_CLOSED
        file.mode = FileNode.MODE_NONE
        print('File closed successfully!')
    else:
        print('File is not open!')


def exit_program(structure: DirectoryNode, memory: Memory):
    print('Persisting data...')

    file_io.save_to_file(structure=structure, memory=memory)
    exit(0)
