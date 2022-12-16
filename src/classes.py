import datetime
import math
import string
from abc import ABC
import sys
from typing import Dict, List

import constants
import utils


class Memory:
    OFFSET_BITS = int(math.log2(constants.BLOCK_SIZE))
    BLOCK_BITS = int(math.log2(constants.TOTAL_BLOCKS))

    def __init__(self, total_size=constants.TOTAL_MEMORY_SIZE) -> None:
        self.space_used = 0
        self.total_size = int(total_size)
        self.memory: List[List[int]] = [[0] * constants.BLOCK_SIZE
                                        for _ in range(constants.TOTAL_BLOCKS)]

        # addr -> size
        # addr [4 bits for block number, self.OFFSET_BITS bits for offset]
        self.allocations: Dict[int, int] = {}
        self.used_per_allocation: Dict[int, int] = {}
        self.free_blocks = [i for i in range(constants.TOTAL_BLOCKS)]

    def allocate(self, size: int):
        if self.space_used + size > self.total_size:
            raise ValueError('Not enough space in memory')

        if size > constants.MAX_FILE_SIZE:
            raise ValueError(
                f'File size too large (max {constants.MAX_FILE_SIZE} bytes)')

        if len(self.free_blocks) == 0:
            raise ValueError('No free blocks available')

        block = self.free_blocks.pop(0)
        addr = block << self.OFFSET_BITS

        self.allocations[addr] = size
        self.used_per_allocation[addr] = 0
        self.space_used += size

        return addr

    def read_file(self, addr: int, starting_byte=0, num_bytes=None):
        size = self.allocations[addr]
        if num_bytes is None:
            num_bytes = self.used_per_allocation[addr]

        block = addr >> self.OFFSET_BITS
        offset = addr & ((2 ** self.OFFSET_BITS) - 1)

        return self.memory[block][offset + starting_byte:offset + starting_byte + num_bytes]

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

        block = addr >> self.OFFSET_BITS
        offset = addr & ((2 ** self.OFFSET_BITS) - 1)

        # self.memory[block][offset:len(data)] = data
        self.memory[block] = self.memory[block][:offset] + \
            data + self.memory[block][offset + len(data):]
        self.used_per_allocation[addr] = len(data)
        return addr

    def append_file(self, addr: int, data: List[int]):
        new_addr = addr
        previous_data_length = self.used_per_allocation[addr]
        if previous_data_length + len(data) > self.allocations[addr]:
            new_addr = self.reallocate(addr, previous_data_length + len(data))

        previous_data = self.read_file(addr, 0, previous_data_length)
        return self.write_file(new_addr, previous_data + data)

    def move_within_file(self, addr: int, starting_byte: int, content_length: int, writing_byte: int):
        if starting_byte + content_length > self.allocations[addr]:
            raise ValueError(
                'Starting byte + content length must be less than or equal to file size')

        if writing_byte + content_length > self.allocations[addr]:
            raise ValueError(
                'Writing byte + content length must be less than or equal to file size')

        block = addr >> self.OFFSET_BITS
        offset = addr & ((2 ** self.OFFSET_BITS) - 1)

        data = self.read_file(addr, starting_byte,
                              starting_byte + content_length)

        self.memory[block][offset + writing_byte:offset +
                           writing_byte + content_length] = data

        return addr

    def reallocate(self, addr: int, new_size: int):
        if self.space_used - self.allocations[addr] + new_size > self.total_size:
            raise ValueError('Not enough space in memory')

        self.deallocate(addr)
        return self.allocate(new_size)

    def deallocate(self, addr: int):
        size = self.allocations.get(addr, None)
        if size is None:
            return

        block = addr >> self.OFFSET_BITS
        self.space_used -= size
        del self.allocations[addr]
        del self.used_per_allocation[addr]
        self.free_blocks.append(block)

    def get_free_space(self):
        return self.total_size - self.space_used

    def show_memory_map(self, outfile=sys.stdout):
        print("Memory Map:", file=outfile)
        for i, (addr, size) in enumerate(self.allocations.items()):
            print(
                f"Allocation#{i+1} | Address: {addr}, Size: {size}, Used: {self.used_per_allocation[addr]}", file=outfile)

    def show_memory_layout(self, outfile=sys.stdout):
        print("Memory Layout:", file=outfile)
        for i, block in enumerate(self.memory):
            print(f"Block {i}: {block}", file=outfile)

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
        memory.allocations = {
            int(addr): size for addr,
            size in data['allocations'].items()
        }
        memory.used_per_allocation = {
            int(addr): size for addr,
            size in data['used_per_allocation'].items()
        }
        memory.memory = data['memory']
        return memory


class FS_Node(ABC):
    memory: Memory

    def __init__(self, name: string, date_created: datetime) -> None:
        self.name = name
        self.date_created = date_created
        self.parent: FS_Node = None

    def print_directory_structure(self, level=0, max_level=10):
        if level > max_level:
            return

        print('\t' * level,
              '--',
              utils.TColors.OKCYAN + utils.TColors.BOLD if isinstance(
                  self, DirectoryNode) else '',
              self.name,
              utils.TColors.ENDC)
        if isinstance(self, DirectoryNode):
            for child in self.children:
                child.print_directory_structure(level + 1, max_level)

    def __dict__(self):
        return self.name

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_dict(cls, data):
        return data.get('type') == DirectoryNode.__name__ and DirectoryNode.from_dict(data) or FileNode.from_dict(data)


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
        # child.__del__()

    def get_child(self, name: str):
        for child in self.children:
            if child.name == name:
                return child

        return None

    def __dict__(self):
        return {
            'name': self.name,
            'date_created': str(self.date_created),
            'parent': str(self.parent) if self.parent else None,
            'children': self.children,

            'type': __class__.__name__
        }

    def __str__(self) -> str:
        return super().__str__()

    def __del__(self):
        # print('Deleting', self.name)
        for child in self.children:
            child.__del__()

    @classmethod
    def from_dict(cls, data):
        dir = DirectoryNode(
            data['name'], utils.get_datetime_object(data['date_created']))

        for child in data['children']:
            if child['type'] == FileNode.__name__:
                dir.add_child(FileNode.from_dict(child))
            elif child['type'] == DirectoryNode.__name__:
                dir.add_child(DirectoryNode.from_dict(child))

        return dir


class FileNode(FS_Node):
    def __init__(self, name: string, date_created: datetime = datetime.datetime.now(), date_modified: datetime = datetime.datetime.now()) -> None:
        super().__init__(name, date_created)
        self.date_modified = date_modified
        self.starting_addr = -1
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
            'date_created': str(self.date_created),
            'date_modified': str(self.date_modified),
            'parent': str(self.parent) if self.parent else None,
            'starting_addr': self.starting_addr,
            'size': self.size,

            'type': __class__.__name__
        }

    def __str__(self) -> str:
        return super().__str__()

    def __del__(self):
        if self.starting_addr != -1 and self.size != 0:
            FS_Node.memory.deallocate(self.starting_addr)
            # print('Deallocated memory', self.starting_addr)

    @classmethod
    def from_dict(cls, data):
        file = FileNode(data['name'], utils.get_datetime_object(
            data['date_created']), utils.get_datetime_object(data['date_modified']))
        file.parent = data['parent']
        file.starting_addr = data['starting_addr']
        file.size = data['size']

        return file
