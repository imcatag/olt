from enum import Enum
from time import sleep
from typing import List
from collections import deque
from random import shuffle, choice, uniform, randint
from copy import deepcopy

class Piece(Enum):
    I = 0
    J = 1
    L = 2
    O = 3
    S = 4
    T = 5
    Z = 6
    NULLPIECE = 7

weights = {'lineClears' : [0, -2, -2, -2, 15], 'TSpin' : [0, 5, 15, 25] , 'TSpinMini' : [0, 0, 0], 'wellKnown' : 6, 'perfectClear' : 30, 'height': 0, 'overHalf': -0.12, 'spikiness' : -0.5, 'covered' : -1, 'gaps' : -2, 'wastedT' : -2}

class Vector2Int:
    # has x and y
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, other: 'Vector2Int') -> 'Vector2Int':
        return Vector2Int(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2Int') -> 'Vector2Int':
        return Vector2Int(self.x - other.x, self.y - other.y)
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__ (self, other) -> bool:
        # if other is not Vector2Int or Tuple, return False
        if not isinstance(other, (Vector2Int, tuple)):
            return False
        # if other is tuple, convert to Vector2Int
        if isinstance(other, tuple):
            other = Vector2Int(other[0], other[1])
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))

spawnPosition = Vector2Int(4, 20)
globalWidth = 10
globalHeight = 40

defaultbag = [Piece.T, Piece.J, Piece.Z, Piece.O, Piece.S, Piece.L, Piece.I]
pieceQueue = []

for i in range(200000):
    shuffle(defaultbag)
    pieceQueue += defaultbag

Cells = {
    Piece.I: [
        [Vector2Int(-1, 1), Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(2, 1)],
        [Vector2Int(1, -1), Vector2Int(1, 0), Vector2Int(1, 1), Vector2Int(1, 2)],
        [Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(2, 0)],
        [Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(0, 2)]
    ],
    Piece.J: [ # TODO: J piece and L piece are the other way round?
        [Vector2Int(-1, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0)],
        [Vector2Int(1, 1), Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(0, -1)],
        [Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, -1)],
        [Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(0, -1), Vector2Int(-1, -1)]
    ],
    Piece.L: [
        [Vector2Int(1, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0)],
        [Vector2Int(1, -1), Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(0, 1)],
        [Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(-1, -1)],
        [Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(-1, 1)]
    ],
    Piece.O: [
        [Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)],
        [Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)],
        [Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)],
        [Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)]
    ],
    Piece.S: [ # TODO: S piece and Z piece are reversed?
        [Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(-1, 0), Vector2Int(0, 0)],
        [Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, -1)],
        [Vector2Int(-1, -1), Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(1, 0)],
        [Vector2Int(-1, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(0, -1)]
    ],
    Piece.T: [
        [Vector2Int(0, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0)],
        [Vector2Int(1, 0), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(0, -1)],
        [Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(0, -1)],
        [Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(0, -1)]
    ],
    Piece.Z: [
        [Vector2Int(-1, 1), Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(1, 0)],
        [Vector2Int(1, 1), Vector2Int(1, 0), Vector2Int(0, 0), Vector2Int(0, -1)],
        [Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(0, -1), Vector2Int(1, -1)],
        [Vector2Int(-1, -1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(0, 1)]
    ]
}

WallKicksI = [
    [Vector2Int(0, 0), Vector2Int(-2, 0), Vector2Int(1, 0), Vector2Int(-2, -1), Vector2Int(1, 2)],  # 0 -> 1
    [Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(2, 0), Vector2Int(-1, 2), Vector2Int(2, -1)],  # 1 -> 2
    [Vector2Int(0, 0), Vector2Int(2, 0), Vector2Int(-1, 0), Vector2Int(2, 1), Vector2Int(-1, -2)],  # 2 -> 3
    [Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(-2, 0), Vector2Int(1, -2), Vector2Int(-2, 1)]   # 3 -> 0
]

CounterWallKicksI = [
    [Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(2, 0), Vector2Int(-1, 2), Vector2Int(2, -1)],  # 0 -> 3
    [Vector2Int(0, 0), Vector2Int(2, 0), Vector2Int(-1, 0), Vector2Int(2, 1), Vector2Int(-1, -2)],  # 1 -> 0
    [Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(-2, 0), Vector2Int(1, -2), Vector2Int(-2, 1)],  # 2 -> 1
    [Vector2Int(0, 0), Vector2Int(-2, 0), Vector2Int(1, 0), Vector2Int(-2, -1), Vector2Int(1, 2)]   # 3 -> 2
]

WallKicksJLOSTZ = [
    [Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(-1, 1), Vector2Int(0, -2), Vector2Int(-1, -2)],  # 0 -> 1
    [Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, -1), Vector2Int(0, 2), Vector2Int(1, 2)],     # 1 -> 2
    [Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, 1), Vector2Int(0, -2), Vector2Int(1, -2)],    # 2 -> 3
    [Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(-1, -1), Vector2Int(0, 2), Vector2Int(-1, 2)]   # 3 -> 0
]

CounterWallKicksJLOSTZ = [
    [Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, 1), Vector2Int(0, -2), Vector2Int(1, -2)],     # 0 -> 3
    [Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, -1), Vector2Int(0, 2), Vector2Int(1, 2)],     # 1 -> 0
    [Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(-1, 1), Vector2Int(0, -2), Vector2Int(-1, -2)],  # 2 -> 1
    [Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(-1, -1), Vector2Int(0, 2), Vector2Int(-1, 2)]    # 3 -> 2
]

Flips = [
    [Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(-1, 1), Vector2Int(1, 0), Vector2Int(-1, 0)],  # 0 -> 2
    [Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, 2), Vector2Int(1, 1), Vector2Int(0, 2), Vector2Int(0, 1)],  # 1 -> 3
    [Vector2Int(0, 0), Vector2Int(0, -1), Vector2Int(-1, -1), Vector2Int(1, -1), Vector2Int(-1, 0), Vector2Int(1, 0)],  # 2 -> 0
    [Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(-1, 2), Vector2Int(-1, 1), Vector2Int(0, 2), Vector2Int(0, 1)]   # 3 -> 1
]

TSpinFacingCorners = [[Vector2Int(-1, 1), Vector2Int(1, 1)],
        [Vector2Int(1, 1), Vector2Int(1, -1)],

        [Vector2Int(1, -1), Vector2Int(-1, -1)],
        [Vector2Int(-1, -1), Vector2Int(-1, 1)]]

Diagonals = [Vector2Int(-1, 1),
        Vector2Int(1, 1),
        Vector2Int(1, -1),
        Vector2Int(-1, -1)]


class Move:
    def __init__(self, type: str, offset = 0):
        self.type = type
        self.offset = offset

    def __str__(self) -> str:
        return f"{self.type} {self.offset}"
    
    def __repr__(self) -> str:
        return f"({self.type}, {self.offset})"

class Placement:
    def __init__(self, piece: Piece, rotation: int, position: Vector2Int, path : List[Move] = []):
        self.piece = piece
        self.rotation = rotation
        self.position = position
        self.path = path

class Board:
    def __init__(self, width: int = globalWidth, height: int = globalHeight, board: List[List[int]] = None):
        self.width = width
        self.height = height
        if board is None:
            self.board = [[0 for _ in range(width)] for _ in range(height)]
        else:
            self.board = deepcopy(board)
            # add lines to board if not enough lines
            while len(self.board) < height:
                self.board += [[0 for _ in range(width)]]

    def maxHeight(self) -> int:
        for i in range(self.height - 1, -1, -1):
            for j in range(self.width):
                if self.board[i][j] == 1:
                    return i + 1
        return 0
    
    def __str__(self) -> str:
        result = ""
        for i in range(self.height//2 - 1, -1, -1):  # // 2 to only show bottom half, which player should see
            for j in range(self.width):
                if self.board[i][j] == 1:
                    result += "#"
                else:
                    result += "_"
            result += "\n"

        return result
    
    def isValid(self, piece: Piece, postion: Vector2Int, rotation: int) -> bool:
        for i in range(4):
            cell = postion + Cells[piece][rotation][i]
            if cell.x < 0 or cell.x >= self.width or cell.y < 0 or cell.y >= self.height:
                return False
            if self.board[cell.y][cell.x] == 1:
                return False
        return True
    
    def findPlacements(self, piece: Piece, held: bool = False) -> List[Placement]:

        finalPlacements = []

        if piece == Piece.NULLPIECE:
            print("Just tried to find placements for a null piece")
            return []
        
        # if spawn of piece is obstructed, return empty list

        if not self.isValid(piece, spawnPosition, 0):
            return []

        maxHeight = self.maxHeight()

        optimalSpawnPosition = Vector2Int(spawnPosition.x, min(spawnPosition.y, maxHeight + 2))

        path1 = []

        if held:
            path1.append(Move("H"))
        
        for i in range(optimalSpawnPosition.y, spawnPosition.y + 1):
            path1.append(Move("S"))

        # visited is [4][width+2][height+2]
        offset = 2
        visited = [[[False for _ in range(self.height + 4)] for _ in range(self.width + 4)] for _ in range(4)]

        queue = deque()
        queue.append(Placement(piece, 0, optimalSpawnPosition, path1))

        while len(queue) > 0:
            currentPlacement = queue.popleft()

            if visited[currentPlacement.rotation][currentPlacement.position.x + offset][currentPlacement.position.y + offset]:
                continue

            visited[currentPlacement.rotation][currentPlacement.position.x + offset][currentPlacement.position.y + offset] = True

            # add to final placements if cannot move down
            if not self.isValid(currentPlacement.piece, currentPlacement.position + Vector2Int(0, -1), currentPlacement.rotation):
                finalPlacements.append(currentPlacement)
            else:
                # move down
                queue.append(Placement(currentPlacement.piece, currentPlacement.rotation, currentPlacement.position + Vector2Int(0, -1), currentPlacement.path + [Move("D")]))
            
            # move left
            if self.isValid(currentPlacement.piece, currentPlacement.position + Vector2Int(-1, 0), currentPlacement.rotation):
                queue.append(Placement(currentPlacement.piece, currentPlacement.rotation, currentPlacement.position + Vector2Int(-1, 0), currentPlacement.path + [Move("L")]))
            
            # move right
            if self.isValid(currentPlacement.piece, currentPlacement.position + Vector2Int(1, 0), currentPlacement.rotation):
                queue.append(Placement(currentPlacement.piece, currentPlacement.rotation, currentPlacement.position + Vector2Int(1, 0), currentPlacement.path + [Move("R")]))

            # rotate clockwise
            newRotation = (currentPlacement.rotation + 1) % 4
            newCells = Cells[currentPlacement.piece][newRotation]
            offsetList = WallKicksI[currentPlacement.rotation] if currentPlacement.piece == Piece.I else WallKicksJLOSTZ[currentPlacement.rotation]

            for i in range(5):
                newPosition = currentPlacement.position + offsetList[i]
                if self.isValid(currentPlacement.piece, newPosition, newRotation):
                    queue.append(Placement(currentPlacement.piece, newRotation, newPosition, currentPlacement.path + [Move("CW", i)]))
                    break
                
            # rotate counterclockwise
            newRotation = (currentPlacement.rotation + 3) % 4
            newCells = Cells[currentPlacement.piece][newRotation]
            offsetList = CounterWallKicksI[currentPlacement.rotation] if currentPlacement.piece == Piece.I else CounterWallKicksJLOSTZ[currentPlacement.rotation]

            for i in range(5):
                newPosition = currentPlacement.position + offsetList[i]
                if self.isValid(currentPlacement.piece, newPosition, newRotation):
                    queue.append(Placement(currentPlacement.piece, newRotation, newPosition, currentPlacement.path + [Move("CCW", i)]))
                    break

            # rotate 180
                    
            newRotation = (currentPlacement.rotation + 2) % 4
            newCells = Cells[currentPlacement.piece][newRotation]
            offsetList = Flips[currentPlacement.rotation]

            for i in range(6):
                newPosition = currentPlacement.position + offsetList[i]
                if self.isValid(currentPlacement.piece, newPosition, newRotation):
                    queue.append(Placement(currentPlacement.piece, newRotation, newPosition, currentPlacement.path + [Move("180", i)]))
                    break
            
        return finalPlacements

    def addGarbage(self, lines):
        hole = randint(0, self.width - 1)
        line = [1 if j != hole else 0 for j in range(self.width)]
        lines = [deepcopy(line) for _ in range(lines)]
        self.board = lines + self.board[:-len(lines)]

def PlacePieceAndEvaluate(board: Board, placement: Placement) -> (Board, float, List[float], int, int):
    newBoard = Board(board.width, board.height, board.board)
    score = 0

    # place piece
    for i in range(4):
        cell = placement.position + Cells[placement.piece][placement.rotation][i]
        newBoard.board[cell.y][cell.x] = 1

    # if piece is T and last move was rotation, check for T-Spin
    tspin = False
    tspinmini = False
    wastedT = False
    if placement.piece == Piece.T:
        wastedT = True

    if placement.piece == Piece.T and (placement.path[-1].type == "CW" or placement.path[-1].type == "CCW"):
        # check for fin and overhang T-Spin
        if (placement.rotation == 3 or placement.rotation == 1) and placement.path[-1].offset == 4:
            tspin = True
        else:
            # get number of corners filled
            cornersFilled = 0
            for offset in Diagonals:
                # if out of bounds, add to corners filled
                if placement.position.x + offset.x < 0 or placement.position.x + offset.x >= newBoard.width or placement.position.y + offset.y < 0 or placement.position.y + offset.y >= newBoard.height:
                    cornersFilled += 1
                
                # if not out of bounds, check if filled
                elif newBoard.board[placement.position.y + offset.y][placement.position.x + offset.x] == 1:
                    cornersFilled += 1
            
            # get number of facing corners filled
            facingCornersFilled = 0
            for offset in TSpinFacingCorners[placement.rotation]:
                # if out of bounds, add to corners filled
                if placement.position.x + offset.x < 0 or placement.position.x + offset.x >= newBoard.width or placement.position.y + offset.y < 0 or placement.position.y + offset.y >= newBoard.height:
                    facingCornersFilled += 1
                
                # if not out of bounds, check if filled
                elif newBoard.board[placement.position.y + offset.y][placement.position.x + offset.x] == 1:
                    facingCornersFilled += 1
                
            # if 3 corners filled, T-Spin
            if cornersFilled >= 3:
                if facingCornersFilled >= 2:
                    tspin = True
                else:
                    tspinmini = True
    
    # clear lines
    maxHeight = newBoard.maxHeight()
    shouldClear = [True for _ in range(maxHeight)]
    linesCleared = 0
    

    for i in range(maxHeight):
        for j in range(newBoard.width):
            if newBoard.board[i][j] == 0:
                shouldClear[i] = False
                break

    for i in range(maxHeight - 1, -1, -1):
        if shouldClear[i]:
            linesCleared += 1
            newBoard.board.pop(i)
    
    newBoard.board += [[0 for _ in range(newBoard.width)] for _ in range(linesCleared)]

    maxHeight = newBoard.maxHeight()

    # check for perfect clear - if bottom line is empty, perfect clear
    perfectClear = 1 not in newBoard.board[0]

    # calculate spikiness
    
    # get heights
    heights = [0 for _ in range(newBoard.width)]
    for i in range(newBoard.width):
        for j in range(maxHeight - 1, -1, -1):
            if newBoard.board[j][i] == 1:
                heights[i] = j + 1
                break
    
    # calculate spikiness
    spikiness = 0
    for i in range(newBoard.width - 1):
        spikiness += max(abs(heights[i] - heights[i + 1]) - 1, 0)

    # calculate 0s covered by 1s
    found1 = [False for _ in range(newBoard.width)]
    covered = 0

    for i in range(maxHeight - 1, -1, -1):
        for j in range(newBoard.width):
            if newBoard.board[i][j] == 1:
                found1[j] = True
            elif found1[j]:
                covered += 1

    gaps = 0
    # calculate 0s with 1s right above
    for i in range(maxHeight - 2, -1, -1):
        for j in range(newBoard.width):
            gaps += (newBoard.board[i][j] == 0) and (newBoard.board[i+1][j] == 1)

    # calculate 1s over half height
    overHalf = 0
    for i in range(newBoard.width):
        overHalf += max(0, heights[i] - maxHeight//2)

    # look for well knows T spin setups
    # 101
    # 000
    # 100
    # OR
    # 101
    # 000
    # 001
    wellKnown = False
    for i in range(maxHeight - 2, -1, -1):
        for j in range(newBoard.width - 2):
            # do the 9 checks
            if newBoard.board[i][j] == 1 and newBoard.board[i][j+1] == 0 and newBoard.board[i][j+2] == 1 and newBoard.board[i+1][j] == 0 and newBoard.board[i+1][j+1] == 0 and newBoard.board[i+1][j+2] == 0 and newBoard.board[i+2][j] == 1 and newBoard.board[i+2][j+1] == 0 and newBoard.board[i+2][j+2] == 0:
                wellKnown = True
                break
            if newBoard.board[i][j] == 1 and newBoard.board[i][j+1] == 0 and newBoard.board[i][j+2] == 1 and newBoard.board[i+1][j] == 0 and newBoard.board[i+1][j+1] == 0 and newBoard.board[i+1][j+2] == 0 and newBoard.board[i+2][j] == 0 and newBoard.board[i+2][j+1] == 0 and newBoard.board[i+2][j+2] == 1:
                wellKnown = True
                break

    features = [linesCleared, spikiness, covered, gaps, maxHeight, perfectClear, -1 if not tspin else linesCleared, 0 if not tspinmini else linesCleared]
    score = weights['spikiness'] * spikiness + weights['covered'] * covered + weights['height'] * maxHeight + weights['overHalf'] * overHalf + perfectClear * weights['perfectClear'] + gaps * weights['gaps'] + wellKnown * weights['wellKnown']
    linesSent = 0
    if tspin:
        score += weights['TSpin'][linesCleared]
        if linesCleared:
            with open("tspins.txt", "a") as f:
                f.write(str(board))
                f.write("\n")
                f.write(str(newBoard))
                f.write("\n")
                f.write(str(placement.path))
                f.write("\n")
                f.write("\n")
            wastedT = False
            linesSent = linesCleared * 2
    elif tspinmini:
        score += weights['TSpinMini'][linesCleared]
        linesSent = linesCleared
    else:
        score += weights['lineClears'][linesCleared]
        if linesCleared == 2:
            linesSent = 1
        elif linesCleared == 3:
            linesSent = 2
        elif linesCleared == 4:
            linesSent = 4
    if perfectClear:
        linesSent += 10
    score += weights['wastedT'] * wastedT
    # 1/20 chance to recieve 4 lines of garbage
    # 1/10 chance to recieve 1 line of garbage

    # recieved4 = uniform(0, 1) < 1/50
    # recieved1 = uniform(0, 1) < 1/50

    # if recieved4 and linesCleared < 4:
    #     garbageHole = randint(0, newBoard.width - 1)
    #     garbageLine = [1 for i in range(newBoard.width)]
    #     garbageLine[garbageHole] = 0

    #     garbageLines = [deepcopy(garbageLine) for i in range(4)]
    #     newBoard.board = (garbageLines + newBoard.board)[:-4]

    # if recieved1 and linesCleared == 0:
    #     garbageHole = randint(0, newBoard.width - 1)
    #     garbageLine = [1 for i in range(newBoard.width)]
    #     garbageLine[garbageHole] = 0

    #     newBoard.board = ([deepcopy(garbageLine)] + newBoard.board)[:-1]

    return (newBoard, score, features, linesCleared, linesSent)

class GameState:
    def __init__(self, board: Board, piece: Piece, heldPiece: Piece = Piece.NULLPIECE, pieceCount: int = 0, evaluation : float = 0, features: List[float] = [], clearing : int = 0, sending : int = 0):
        self.board = board
        self.piece = piece
        self.heldPiece = heldPiece
        self.pieceCount = pieceCount
        self.evaluation = evaluation
        self.features = features
        self.clearing = clearing
        self.sending = sending
    
    def get_game_repr(self):
        game_state_width = self.board.height // 2
        game_state_repr = [[0] * game_state_width for _ in range(game_state_width)] # make the state repr 20x20 by default

        for i in range(game_state_width):
            for j in range(self.board.width):
                game_state_repr[i][j] = self.board.board[i][j]

        # place current piece and queue pieces
        piece = self.piece
        for i in range(7):
            # start 5 squares to the right of where the initial board ends
            position_for_piece = Vector2Int(self.board.width + 5, i * 2 + 1)
            for j in range(4):
                cell = position_for_piece + Cells[piece][0][j]
                game_state_repr[cell.y][cell.x] = 1
            piece = pieceQueue[self.pieceCount + i + 1]

        # add held piece to the bottom of the board
        if self.heldPiece != Piece.NULLPIECE:
            position_for_hold_piece = Vector2Int(self.board.width + 5, game_state_width - 2)
            for j in range(4):
                cell = position_for_hold_piece + Cells[self.heldPiece][0][j]
                game_state_repr[cell.y][cell.x] = 1
        if len(self.features) == 0:
            return game_state_repr
        
        if self.features[6] == 2:
            # add T-Spin indicator
            for i in range(4):
                game_state_repr[i][-1] = 1
        elif self.features[6] == 3:
            for i in range(6):
                game_state_repr[i][-1] = 1
        elif self.features[0] == 4:
            for i in range(4):
                game_state_repr[i][-1] = 1

        return game_state_repr

    def generateChildren(self) -> List['GameState']:

        children = []

        if self.piece == Piece.NULLPIECE:
            print("Just tried to generate children for a null piece")
            return []
        
        else:
            placements = self.board.findPlacements(self.piece)
            for placement in placements:
                newBoard, newEvaluation, features, linesCleared, linesSent = PlacePieceAndEvaluate(self.board, placement)
                children.append(GameState(newBoard, pieceQueue[self.pieceCount + 1], self.heldPiece, self.pieceCount + 1, newEvaluation, features, linesCleared, linesSent))
                
        
        if self.heldPiece == Piece.NULLPIECE:
            # hold piece becomes current piece, current piece becomes next piece
            newState = GameState(self.board, pieceQueue[self.pieceCount + 1], self.piece, self.pieceCount + 1)

            # create children for newState

            placements = newState.board.findPlacements(newState.piece, True)

            for placement in placements:
                newBoard, newEvaluation, features, linesCleared, linesSent = PlacePieceAndEvaluate(newState.board, placement)
                children.append(GameState(newBoard, pieceQueue[newState.pieceCount + 1], newState.heldPiece, newState.pieceCount + 1, newEvaluation, features, linesCleared, linesSent))

        if self.heldPiece != Piece.NULLPIECE:
            # hold piece becomes current piece, held piece becomes hold piece
            newState = GameState(self.board, self.heldPiece, self.piece, self.pieceCount)

            # create children for newState

            placements = newState.board.findPlacements(newState.piece, True)

            for placement in placements:
                newBoard, newEvaluation, features, linesCleared, linesSent = PlacePieceAndEvaluate(newState.board, placement)
                children.append(GameState(newBoard, pieceQueue[newState.pieceCount + 1], newState.heldPiece, newState.pieceCount + 1, newEvaluation, features, linesCleared, linesSent))

        return children

    def __str__(self) -> str:
        result = self.board.__str__()
        result += f"Piece: {self.piece}\n"
        result += f"Held Piece: {self.heldPiece}\n"
        result += f"Piece Count: {self.pieceCount}\n"
        result += f"Evaluation: {self.evaluation}\n"

        return result

# # create initial board
# board = Board()

# # create initial game state
# gameState = GameState(board, pieceQueue[0])

# # # create initial children
# children = gameState.generateChildren()

# while True:
#     if len(children) == 0:
#         break 
#     # choose child with highest evaluation
#     child = max(children, key = lambda x: x.evaluation)
    
#     # print child
#     for row in child.get_game_repr():
#         print(' '.join(map(str, row)))

#     # generate children for child
#     children = child.generateChildren()

#     print("<-------------------------->")
#     sleep(1)