from enum import Enum


class Status(Enum):
    OFF = 0
    BUSY = 1
    TENTATIVE = 2
    FREE = 3
