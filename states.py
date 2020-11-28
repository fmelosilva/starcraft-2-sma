from enum import Enum

class STATES(Enum):
    IDLE = 1,
    WORKER_BUILDING = 2,
    WORKER_MINERALS = 3,
    WORKER_GAS = 4,
    ARMY_DEFENDING = 5
