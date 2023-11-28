from data import *
from enum import Enum

spawnPosition = Vector2Int(4, 19)

class Node:
    def __init__(self, position: Vector2Int, rotation: int, path: list, ):
        self.position = position
        self.rotation = rotation
        self.path = path

    def __str__(self):
        return f"Position: {self.position}, Rotation: {self.rotation}, Path: {self.path}"

    def __repr__(self):
        return f"Position: {self.position}, Rotation: {self.rotation}, Path: {self.path}"

class Board:
    # size 10 x 40
    # has piece
    def __init__(self, piece: Tetromino, cells = None):
        if cells is not None:
            self.cells = cells
        else:
            self.cells = [[0 for x in range(10)] for y in range(40)]
        self.piece = piece

    def __str__(self):
        # should be upside down
        output = ""
        for y in range(39, -1, -1):
            for x in range(10):
                output += str(self.cells[y][x])
            output += "\n"
        return output
    
    def isValid(self, position: Vector2Int, rotation: int):
        # check if piece is in bounds
        for cell in Cells[self.piece][rotation]:
            posx = position.x + cell.x
            posy = position.y + cell.y
            if posx < 0 or posx >= 10:
                return False
            if posy < 0 or posy >= 40:
                return False
            # check if piece (x, y) is occupied
            if self.cells[posy][posx] != 0:
                return False 
        return True

    def isRotationValid(self, cells: [], position: Vector2Int):
        for cell in cells:
            posx = position.x + cell.x
            posy = position.y + cell.y
            if posx < 0 or posx >= 10:
                return False
            if posy < 0 or posy >= 40:
                return False
            # check if piece (x, y) is occupied
            if self.cells[posy][posx] != 0:
                return False
        return True
    
    def findPlacements(self):
        start = Node(spawnPosition, 0, [])
        # init placements with dictionary for rotation
        # each dictionary has a list of 10x40
        # each element is either None or a Node
        placements = {0: [[None for x in range(10)] for y in range(40)],
                      1: [[None for x in range(10)] for y in range(40)],
                      2: [[None for x in range(10)] for y in range(40)],
                      3: [[None for x in range(10)] for y in range(40)]}
        
        finalPlacements =  {0: [[None for x in range(10)] for y in range(40)],
                            1: [[None for x in range(10)] for y in range(40)],
                            2: [[None for x in range(10)] for y in range(40)],
                            3: [[None for x in range(10)] for y in range(40)]}
        
        # init queue with start
        queue = [start]

        # while queue is not empty

        while len(queue) > 0:
            # if placements[rotation][position] is None, replace with node
            # if placements[rotation][position] is not None, pass

            currentNode = queue.pop(0)
            rotation = currentNode.rotation
            position = currentNode.position
            path = currentNode.path

            if placements[rotation][position.y][position.x] is None:
                placements[rotation][position.y][position.x] = currentNode
            else:
                continue
            
            # if piece cannot move down, add to finalPlacements
            if not self.isValid(position - Vector2Int(0, 1), rotation):
                finalPlacements[rotation][position.y][position.x] = currentNode

            # add valid neighbors to queue
            # down
            if self.isValid(position - Vector2Int(0, 1), rotation):
                queue.append(Node(position - Vector2Int(0, 1), rotation, path + ["S"]))

            # left 
            if self.isValid(position - Vector2Int(1, 0), rotation):
                queue.append(Node(position - Vector2Int(1, 0), rotation, path + ["L"]))
            
            # right
            if self.isValid(position + Vector2Int(1, 0), rotation):
                queue.append(Node(position + Vector2Int(1, 0), rotation, path + ["R"]))

            # rotate clockwise
            newrotation = (rotation + 1) % 4

            newCells = Cells[self.piece][newrotation]

            offsetList = []

            if self.piece == Tetromino.I:
                offsetList = WallKicksI[rotation]            
            else:
                offsetList = WallKicksJLOSTZ[rotation]

            for offset in offsetList:
                if self.isRotationValid(newCells, position + offset):
                    queue.append(Node(position + offset, newrotation, path + ["CW"]))
                    break

            # rotate counterclockwise

            newrotation = (rotation - 1) % 4

            newCells = Cells[self.piece][newrotation]

            offsetList = []

            if self.piece == Tetromino.I:
                offsetList = CounterWallKicksI[rotation]
            else:
                offsetList = CounterWallKicksJLOSTZ[rotation]

            for offset in offsetList:
                if self.isRotationValid(newCells, position + offset):
                    queue.append(Node(position + offset, newrotation, path + ["CCW"]))
                    break

            # flip 180

            newrotation = (rotation + 2) % 4

            newCells = Cells[self.piece][newrotation]

            offsetList = Flips[rotation]

            for offset in offsetList:
                if self.isRotationValid(newCells, position + offset):
                    queue.append(Node(position + offset, newrotation, path + ["180"]))
                    break
        
        return finalPlacements
    
    def findPlacementsAsDict(self):
        start = Node(spawnPosition, 0, [])
        # init placements with dictionary for rotation
        # each dictionary has a list of 10x40
        # each element is either None or a Node
        placements = {0: [[None for x in range(10)] for y in range(40)],
                      1: [[None for x in range(10)] for y in range(40)],
                      2: [[None for x in range(10)] for y in range(40)],
                      3: [[None for x in range(10)] for y in range(40)]}
        
        finalPlacements = {}
        
        # init queue with start
        queue = [start]

        # while queue is not empty

        while len(queue) > 0:
            # if placements[rotation][position] is None, replace with node
            # if placements[rotation][position] is not None, pass

            currentNode = queue.pop(0)
            rotation = currentNode.rotation
            position = currentNode.position
            path = currentNode.path

            if placements[rotation][position.y][position.x] is None:
                placements[rotation][position.y][position.x] = currentNode
            else:
                continue
            
            # if piece cannot move down, add to finalPlacements
            if not self.isValid(position - Vector2Int(0, 1), rotation):
                finalPlacements[(position, rotation)] = path

            # add valid neighbors to queue
            # down
            if self.isValid(position - Vector2Int(0, 1), rotation):
                queue.append(Node(position - Vector2Int(0, 1), rotation, path + ["S"]))

            # left 
            if self.isValid(position - Vector2Int(1, 0), rotation):
                queue.append(Node(position - Vector2Int(1, 0), rotation, path + ["L"]))
            
            # right
            if self.isValid(position + Vector2Int(1, 0), rotation):
                queue.append(Node(position + Vector2Int(1, 0), rotation, path + ["R"]))

            # rotate clockwise
            newrotation = (rotation + 1) % 4

            newCells = Cells[self.piece][newrotation]

            offsetList = []

            if self.piece == Tetromino.I:
                offsetList = WallKicksI[rotation]            
            else:
                offsetList = WallKicksJLOSTZ[rotation]

            for offset in offsetList:
                if self.isRotationValid(newCells, position + offset):
                    queue.append(Node(position + offset, newrotation, path + ["CW"]))
                    break

            # rotate counterclockwise

            newrotation = (rotation - 1) % 4

            newCells = Cells[self.piece][newrotation]

            offsetList = []

            if self.piece == Tetromino.I:
                offsetList = CounterWallKicksI[rotation]
            else:
                offsetList = CounterWallKicksJLOSTZ[rotation]

            for offset in offsetList:
                if self.isRotationValid(newCells, position + offset):
                    queue.append(Node(position + offset, newrotation, path + ["CCW"]))
                    break

            # flip 180

            newrotation = (rotation + 2) % 4

            newCells = Cells[self.piece][newrotation]

            offsetList = Flips[rotation]

            for offset in offsetList:
                if self.isRotationValid(newCells, position + offset):
                    queue.append(Node(position + offset, newrotation, path + ["180"]))
                    break
        
        return finalPlacements
    
    
def displayPath(board: Board, path: list):
    print(board)
    for move in path:
        if move == "S":
            board.piece = board.piece.moveDown()
        elif move == "L":
            board.piece = board.piece.moveLeft()
        elif move == "R":
            board.piece = board.piece.moveRight()
        elif move == "CW":
            board.piece = board.piece.rotateClockwise()
        elif move == "CCW":
            board.piece = board.piece.rotateCounterClockwise()
        elif move == "180":
            board.piece = board.piece.flip180()
        print(board)
board = Board(Tetromino.T)
# set board to have this at the bottom
# 1001110000
# 1000111111
# 1101111111
# this tests for T-Spin Double
line2 = [1, 0, 0, 1, 1, 1, 0, 0, 0, 0]
line1 = [1, 0, 0, 0, 1, 1, 1, 1, 1, 1]
line0 = [1, 1, 0, 1, 1, 1, 1, 1, 1, 1]
board.cells[0] = line0
board.cells[1] = line1
board.cells[2] = line2
placements = board.findPlacementsAsDict()
print(placements)