from datetime import datetime

from classes import FS_Node, DirectoryNode, FileNode, print_directory_structure
from utils import display_menu


def main():
    display_menu()

    root = DirectoryNode('root', datetime.now())
    root.add_child(FileNode('file1', datetime.now()))
    root.add_child(FileNode('file2', datetime.now()))
    root.add_child(FileNode('file3', datetime.now()))
    test_dir = root.add_child(DirectoryNode('test_dir', datetime.now()))

    test_dir.add_child(FileNode('file4', datetime.now()))
    test_dir.add_child(FileNode('file5', datetime.now()))

    FS_Node.print_directory_structure(root)


if __name__ == '__main__':
    main()
