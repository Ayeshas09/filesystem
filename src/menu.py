import time
from datetime import datetime
from typing import List

import file_io
from classes import DirectoryNode, FS_Node, FileNode, Memory
from utils import bytes_to_string, split_strip, string_to_bytes
import csv

menu = {
    'help': 'Display this menu',

    'create <filename>': 'Create a new file',
    'delete <filename | dirname>': 'Remove a file',
    'mkdir <dirname>': 'Create a new directory',
    'chDir <path>': 'Change directory',
    'move <in filename | dirname> <out filename | dirname>': 'Move a file or directory',
    'open <filename>': 'Open a file',
    'close <filename>': 'Close a file',
    'write_to_file <filename>,<content>,<starting offset (optional)>': 'Write to a file',
    'read_from_file <filename> <starting byte> <content length>': 'Read from a file from a specific byte',
    'show_memory_map': 'Show the memory map',
    'truncate <filename>,<size>': 'Truncate a file to a specific size',

    'exit': 'Exit the program'
}


def display_menu():
    print('---------- Available Commands ----------')
    for key, value in menu.items():
        print(f'-- {key}  :  {value}')

    print('----------------------------------------')


def execute_command(command: str, outfile, root: DirectoryNode, memory: Memory):
    currentDir = root

    if command.startswith('exit'):
        exit_program(root, memory, outfile)

    elif command.startswith('create'):
        _, filename = split_strip(command, ' ')

        touch(currentDir, filename, outfile)

    elif command.startswith('delete'):
        _, name = split_strip(command, ' ')
        remove(currentDir, name, outfile)

    elif command.startswith('mkdir'):
        _, dirname = split_strip(command, ' ')
        mkdir(currentDir, dirname, outfile)

    elif command.startswith('chDir'):
        _, path = split_strip(command, ' ')

        currentDir = change_dir(currentDir, path, outfile)

    elif command.startswith('move'):
        _, name, destination = split_strip(command, ' ')
        move(currentDir, name, destination, outfile)

    elif command.startswith('open'):
        _, segments = split_strip(command, ' ')

        filename, _ = segments.split(',')

        if currentDir.get_child(filename):
            print(f"'{filename}' Opened!", file=outfile)
        else:
            print(f"'{filename}' does not exist!", file=outfile)

    elif command.startswith('close'):
        _, filename = split_strip(command, ' ')

        if currentDir.get_child(filename):
            print(f"'{filename}' Closed!", file=outfile)
        else:
            print(f"'{filename}' does not exist!", file=outfile)

    elif command.startswith('write_to_file'):
        segments = split_strip(command, ' ')

        csv_line = ' '.join(segments[1:])

        parsed = list(csv.reader([csv_line], delimiter=','))[0]

        if len(parsed) < 2:
            print('Invalid command', file=outfile)
            return
        filename = parsed[0]
        content = parsed[1]
        starting_offset = int(segments[2]) if len(segments) == 3 else 0

        write_file(currentDir, filename, content, outfile, starting_offset)

    elif command.startswith('read_from_file'):
        segments = split_strip(command, ' ')

        csv_line = ' '.join(segments[1:])
        parsed = list(csv.reader([csv_line], delimiter=','))[0]

        if len(segments) != 3:
            print('Invalid command', file=outfile)
            return

        filename = parsed[0]
        starting_byte = int(parsed[1])
        content_length = int(parsed[2])

        display_file(currentDir, filename, outfile,
                     starting_byte, content_length)

    elif command.startswith('truncate'):
        segments = split_strip(command, ' ')

        csv_line = ' '.join(segments[1:])

        parsed = list(csv.reader([csv_line], delimiter=','))[0]

        if len(segments) != 2:
            print('Invalid command', file=outfile)
            return

        filename = parsed[0]
        new_size = int(parsed[1])

        file_object: FileNode = currentDir.get_child(filename)
        if file_object:
            memory.truncate(file_object.starting_addr, new_size)
            file_object.size = new_size

            print(f"'{filename}' truncated to {new_size} bytes!", file=outfile)
        else:
            print(f"'{filename}' does not exist!", file=outfile)

    elif command.startswith('show_memory_map'):
        memory.show_memory_map(outfile)
        print(file=outfile)

        memory.show_memory_layout(outfile)
        print(file=outfile)

    else:
        print('Invalid command!')


def touch(currentDir, name: str, outfile):
    if currentDir.get_child(name):
        print('File already exists!', file=outfile)

    else:
        new_file = currentDir.add_child(FileNode(name, datetime.now()))
        print('File has been created successfully!', file=outfile)
        return new_file


def remove(currentDir, name, outfile):
    if currentDir.get_child(name):
        child = currentDir.get_child(name)
        currentDir.remove_child(child)
        print('Deleted successfully!', file=outfile)

    else:
        print('No such file or directory exists!', file=outfile)


def mkdir(currentDir, name: str, outfile):
    if currentDir.get_child(name):
        print('Directory already exists!', file=outfile)

    else:
        new_dir = currentDir.add_child(DirectoryNode(name, datetime.now()))
        print('Directory has been created successfully!', file=outfile)
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


def move(currentDir, name, new_name, outfile):
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

        print('Moved successfully!', file=outfile)

    else:
        print('No such file or directory exists!', file=outfile)


def change_dir(currentDir, path, outfile):
    if path == '..':
        return currentDir.parent if currentDir.parent else currentDir

    elif currentDir.get_child(path):
        memory = FS_Node.memory

        newDir = currentDir.get_child(path)
        newDir.memory = memory

        return newDir

    print("No such directory exists", file=outfile)
    return currentDir


def write_file(currentDir: DirectoryNode, filename: str, content: List[str], outfile, starting_offset=0):
    memory = FS_Node.memory

    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!', file=outfile)
        return

    content_bytes = string_to_bytes(content)
    if file.starting_addr < 0 and file.size == 0:
        try:
            file.starting_addr = memory.allocate(len(content_bytes))
            file.size = len(content)
        except ValueError:
            print('Not enough memory!', file=outfile)
            return

    if starting_offset > file.size:
        print('Starting offset is greater than file size!', file=outfile)
        return

    file.starting_addr = memory.write_file(
        file.starting_addr + starting_offset, content_bytes)

    file.date_modified = datetime.now()
    print('File written successfully!', file=outfile)


def append_file(currentDir: DirectoryNode, filename: str, new_content: List[str]):
    memory = FS_Node.memory
    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!')
        return

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


def move_within_file(currentDir: DirectoryNode, filename: str, starting_byte: int, content_length: int, writing_byte: int):
    memory = FS_Node.memory
    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!')
        return

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


def display_file(currentDir: DirectoryNode, filename: str, outfile, starting_byte: int = 0, content_length: int = -1):
    memory = FS_Node.memory
    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!', file=outfile)
        return

    if file.starting_addr < 0 and file.size == 0:
        print(file=outfile)
        return

    content = bytes_to_string(
        memory.read_file(
            file.starting_addr,
            starting_byte=starting_byte,
            num_bytes=file.size if content_length == -1 else content_length)
    )

    print(content, file=outfile)


def exit_program(structure: DirectoryNode, memory: Memory, outfile):
    print('Persisting data...', file=outfile)

    file_io.save_to_file(structure=structure, memory=memory)
    exit(0)
