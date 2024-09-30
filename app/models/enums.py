import enum

class Shapes(enum.Enum): # To define the shapes
    T = 1
    INVERSE_SNAKE = 2
    SNAKE = 3
    STAIRS = 4
    LINE = 5
    L = 6
    INVERSE_L_90 = 7
    L_90 = 8
    TOILET = 9
    Z_90 = 10
    INVERSE_TOILET = 11
    S_90 = 12
    BATON = 13
    INVERSE_BATON = 14
    TURTLE = 15
    U = 16
    PLUS = 17
    DOG = 18
    
class Movements(enum.Enum): # To define the movements
    DIAGONAL = 'Diagonal'
    INVERSE_DIAGONAL = 'Inverse Diagonal'
    LINE = 'Line'
    LINE_BETWEEN = 'Line Between'
    LINE_BORDER = "Line Border"
    L = "L"
    INVERSE_L = "Inverse L"
    
class Colors(enum.Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'

class MatchState(enum.Enum):
    WAITING = "WAITING"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    