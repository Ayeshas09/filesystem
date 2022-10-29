from dataclasses import dataclass
import datetime
import string
from typing import Dict, List
import constants
import math
from abc import ABC


class FS_Node(ABC):
    def __init__(self, name: string, date_created: datetime) -> None:
        self.name = name
        self.date = date_created
        self.parent: FS_Node = None

    def __dict__(self):
        return self.name

    def __str__(self) -> str:
        return self.name


def print_directory_structure(node: FS_Node, level=0, max_level=1):
    if level > max_level:
        return

    print('\t' * level, '--', node.name)
    if isinstance(node, DirectoryNode):
        for child in node.children:
            print_directory_structure(child, level + 1, max_level)


FS_Node.print_directory_structure = staticmethod(print_directory_structure)


class FileNode(FS_Node):
    def __init__(self, name: string, date_created: datetime = datetime.datetime.now(), date_modified: datetime = datetime.datetime.now()) -> None:
        super().__init__(name, date_created)
        self.date_modified = date_modified
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

    def __dict__(self):
        return {
            'name': self.name,
            'date_created': str(self.date),
            'date_modified': str(self.date_modified),
            'parent': str(self.parent) if self.parent else None,
            'starting_addr': self.starting_addr,
            'size': self.size,
        }

    def __str__(self) -> str:
        return super().__str__()


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

    def __dict__(self):
        return {
            'name': self.name,
            'date_created': str(self.date),
            'parent': str(self.parent) if self.parent else None,
            'children': self.children,
        }

    def __str__(self) -> str:
        return super().__str__()

class Memory:
    def __init__(self, total_size=constants.TOTAL_MEMORY_SIZE) -> None:
        self.space_used = 0
        self.total_size = total_size
        # self.curr_ptr = 0
        self.memory = [0] * math.ceil(total_size)

        # starting address -> size
        self.allocations: Dict[int, int] = {}
        self.used_per_allocation: Dict[int, int] = {}

    def allocate(self, size: int):
        if self.space_used + size > self.total_size:
            raise ValueError('Not enough space in memory')

        self.space_used += size

        curr_ptr = 0
        for allocation_addr in sorted(self.allocations.keys()):
            if curr_ptr < allocation_addr:
                if curr_ptr + size <= allocation_addr:
                    self.allocations[curr_ptr] = size
                    return curr_ptr

            curr_ptr = allocation_addr + self.allocations[allocation_addr]

        if curr_ptr + size > self.total_size:
            raise ValueError('Not enough space in memory')

        self.allocations[curr_ptr] = size
        return curr_ptr

    def read_file(self, addr: int, starting_byte=0, num_bytes=None):
        size = self.allocations[addr]
        return self.memory[addr:addr+size][starting_byte:num_bytes]

    def truncate(self, addr: int, new_size: int):
        if new_size > self.allocations[addr]:
            raise ValueError('New size must be smaller than current size')

        self.allocations[addr] = new_size
        self.used_per_allocation[addr] = min(
            self.used_per_allocation[addr], new_size)

    def write_file(self, addr: int, data: List[int]):
        size = self.allocations[addr]
        if len(data) > size:
            addr = self.reallocate(addr, len(data))

        self.memory[addr:addr+size] = data
        self.used_per_allocation[addr] = len(data)
        return addr

    def append_file(self, addr: int, data: List[int]):
        new_addr = addr
        previous_data_length = self.used_per_allocation[addr]
        if previous_data_length + len(data) > self.allocations[addr]:
            new_addr = self.reallocate(addr, previous_data_length + len(data))

        previous_data = self.read_file(addr, 0, previous_data_length)
        return self.write_file(new_addr, previous_data + data)

    def reallocate(self, addr: int, new_size: int):
        if self.space_used - self.allocations[addr] + new_size > self.total_size:
            raise ValueError('Not enough space in memory')

        self.deallocate(addr)
        return self.allocate(new_size)

    def deallocate(self, addr: int):
        size = self.allocations[addr]
        self.space_used -= size
        del self.allocations[addr]

    def get_free_space(self):
        return self.total_size - self.space_used

    def __dict__(self):
        return {
            'space_used': self.space_used,
            'total_size': self.total_size,
            'allocations': self.allocations,
            'used_per_allocation': self.used_per_allocation,
            'memory': self.memory,
        }

    @classmethod
    def from_dict(cls, data):
        memory = cls(data['total_size'])
        memory.space_used = data['space_used']
        memory.allocations = data['allocations']
        memory.used_per_allocation = data['used_per_allocation']
        memory.memory = data['memory']
        return memory
