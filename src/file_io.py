import json
import os
from typing import Tuple

import classes
import constants


def save_to_file(filename=constants.FILENAME, structure: classes.FS_Node = None, memory: classes.Memory = None):
    with open(filename, 'w') as f:
        json.dump({
            'structure': structure,
            'memory': memory
        }, f, default=lambda o: o.__dict__())


def load_from_file(filename=constants.FILENAME) -> Tuple[classes.FS_Node | None, classes.Memory | None]:
    if not os.path.isfile(filename):
        return None, None

    with open(filename, 'r') as f:
        try:
            data = json.load(f)
            memory = classes.Memory.from_dict(data['memory'])
            structure = classes.FS_Node.from_dict(data['structure'])

        except json.decoder.JSONDecodeError or KeyError:
            structure = None
            memory = None

        return structure, memory
