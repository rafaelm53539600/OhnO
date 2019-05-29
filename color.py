from enum import Enum
class COLOR(Enum):
    GRAY = 0
    BLUE = 1
    RED = 2
    def succ(self):
        return COLOR((self.value+1)%3)

