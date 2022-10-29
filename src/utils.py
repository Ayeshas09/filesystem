import string
from datetime import datetime

from classes import DirectoryNode, FileNode


def touch(currentDir, name: string):
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
        del child
        print('Deleted successfully!')

    else:
        print('No such file or directory exists!')


def mkdir(currentDir, name: string):
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
        return currentDir.parent

    elif currentDir.get_child(path):
        return currentDir.get_child(path)

    print("No such directory exists")


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
    print('########## Available commands ##########')
    for key, value in menu.items():
        print(f'-- {key}  :  {value}')

    print('########################################')


def user_input():

    root = DirectoryNode('root', datetime.now())
    currentDir = root

    while True:
        command = input('Enter the command: ')

        if command.lower() == 'exit':
            break

        elif 'touch' in command:
            _, name = command.split(' ')
            touch(currentDir, name)

        elif 'mkdir' in command:
            _, name = command.split(' ')
            mkdir(currentDir, name)

        elif 'ls' in command:
            # FS_Node.print_directory_structure(currentDir)
            currentDir.print_directory_structure()

        elif 'rm' in command:
            _, name = command.split(' ')
            remove(currentDir, name)

        elif 'mv' in command:
            _, name, destination = command.split(' ')
            move(currentDir, name, destination)

        elif 'cd' in command:
            _, path = command.split(' ')

            currentDir = change_dir(currentDir, path)


def string_to_bytes(string):
    return list([ord(char) for char in string])


def bytes_to_string(bytes):
    return ''.join([chr(byte) for byte in bytes])


def get_datetime_object(date_string: str):
    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
