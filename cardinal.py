# Enumeraton is important!
from enum import Enum
class CARDINAL(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    def opposite(self):
        return CARDINAL((self.value +2 )%4)

