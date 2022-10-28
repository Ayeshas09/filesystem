
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


def string_to_bytes(string):
    return list([ord(char) for char in string])


def bytes_to_string(bytes):
    return ''.join([chr(byte) for byte in bytes])

