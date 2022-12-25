import math

FILENAME = './storage.dat'

# 1 KB
TOTAL_MEMORY_SIZE: int = int(math.pow(2, 10))
# 64 B
BLOCK_SIZE: int = int(math.pow(2, 6))
# 16
TOTAL_BLOCKS: int = TOTAL_MEMORY_SIZE // BLOCK_SIZE

# 64 KB
MAX_FILE_SIZE: int = BLOCK_SIZE
