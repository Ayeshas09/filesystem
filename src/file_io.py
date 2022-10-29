import json
from typing import Tuple

import classes
import constants


def save_to_file(filename=constants.FILENAME, structure: classes.FS_Node = None, memory: classes.Memory = None):
    with open(filename, 'w') as f:
        json.dump({
            'structure': structure,
            'memory': memory
        }, f, default=lambda o: o.__dict__())


def load_from_file(filename=constants.FILENAME) -> Tuple[classes.FS_Node, classes.Memory]:
    with open(filename, 'r') as f:
        data = json.load(f)

        return classes.FS_Node.from_dict(data['structure']), classes.Memory.from_dict(data['memory'])
