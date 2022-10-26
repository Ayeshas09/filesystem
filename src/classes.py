import datetime
import string
from typing import List
import constants


class FS_Node:
    def __init__(self, name: string, date_created: datetime) -> None:
        self.name = name
        self.date = date_created
        self.parent: FS_Node = None


def print_directory_structure(node: FS_Node, level=0):
    print('\t' * level, '--', node.name)
    if isinstance(node, DirectoryNode):
        for child in node.children:
            print_directory_structure(child, level + 1)


FS_Node.print_directory_structure = staticmethod(print_directory_structure)


class FileNode(FS_Node):
    def __init__(self, name: string, date_created: datetime) -> None:
        super().__init__(name, date_created)
        self.starting_addr = 0
        self.size = 0

    def set_size(self, size):
        if 0 <= size < constants.MAX_FILE_SIZE:
            self.size = size

        raise ValueError(
            f'File size must be between 0 and {constants.MAX_FILE_SIZE / 1024} KB')

    def set_starting_addr(self, addr):
        if 0 <= addr < constants.TOTAL_MEMORY_SIZE:
            self.starting_addr = addr

        raise ValueError(
            f'Starting address must be between 0 and {constants.TOTAL_MEMORY_SIZE / 1024} KB')


class DirectoryNode(FS_Node):
    def __init__(self, name: string, date_created: datetime) -> None:
        super().__init__(name, date_created)
        self.children: List[FS_Node] = []

    def add_child(self, child: FS_Node) -> FS_Node:
        self.children.append(child)
        child.parent = self
        return child

    def remove_child(self, child: FS_Node):
        self.children.remove(child)

    def get_child(self, name: str):
        for child in self.children:
            if child.name == name:
                return child

        return None


class Memory:
    def __init__(self, total_size=constants.TOTAL_MEMORY_SIZE) -> None:
        self.space_used = 0
        self.total_size = total_size
        self.curr_ptr = 0

        self.allocations = {}

    def allocate(self, size):
        if self.space_used + size > self.total_size:
            raise ValueError('Not enough space in memory')

        self.space_used += size
        addr = self.curr_ptr
        self.curr_ptr += size

        self.allocations[addr] = size
        return addr

    def deallocate(self, addr):
        size = self.allocations[addr]
        self.space_used -= size
        del self.allocations[addr]

    def get_free_space(self):
        return self.total_size - self.space_used
