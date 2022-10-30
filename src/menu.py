import time
from datetime import datetime
from typing import List

import file_io
from classes import DirectoryNode, FileNode, Memory
from utils import bytes_to_string, split_strip, string_to_bytes


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


def write_file(currentDir: DirectoryNode, filename: str, content: List[str], memory: Memory):
    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!')
        return

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


def display_file(currentDir: DirectoryNode, filename: str, memory: Memory):
    file: FileNode = currentDir.get_child(filename)

    if not file or not isinstance(file, FileNode):
        print('No such file exists!')
        return

    if file.starting_addr < 0 and file.size == 0:
        print()
        return

    content = bytes_to_string(memory.read_file(
        file.starting_addr, num_bytes=file.size))

    print(content)


def exit_program(structure: DirectoryNode, memory: Memory):
    print('Persisting data...')
    time.sleep(0.5)

    file_io.save_to_file(structure=structure, memory=memory)
    exit(0)


menu = {
    'touch <filename>': 'Create a new file',
    'rm <filename | dirname>': 'Remove a file',
    'mkdir <dirname>': 'Create a new directory',
    'cd <path>': 'Change directory',
    'mv <in filename | dirname> <out filename | dirname>': 'Move a file or directory',
    'wf <filename> <content>': 'Write to a file',
    'cat <filename>': 'Read from a file',
    'ls <path>': 'List files and directories',
    'exit': 'Exit the program'
}


def display_menu():
    print('---------- Available commands ----------')
    for key, value in menu.items():
        print(f'-- {key}  :  {value}')

    print('----------------------------------------')


def user_input(root: DirectoryNode, memory: Memory):

    currentDir = root

    while True:
        command = input('Enter the command: ').strip()

        if command.startswith('exit'):
            exit_program(root, memory)

        elif command.startswith('touch'):
            _, filename = split_strip(command, ' ')
            touch(currentDir, filename)

        elif command.startswith('mkdir'):
            _, dirname = split_strip(command, ' ')
            mkdir(currentDir, dirname)

        elif command.startswith('ls'):
            currentDir.print_directory_structure()

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

            write_file(currentDir, filename, content, memory)

        elif command.startswith('cat'):
            _, filename = split_strip(command, ' ')

            display_file(currentDir, filename, memory)
