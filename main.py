from data import *
from enum import Enum
from copy import deepcopy
from random import randint, choice, shuffle
spawnPosition = Vector2Int(4, 19)

fitnessMultipliers = {'linesCleared': [0, 500, 500, 500, 10000], 'tSpin': 20, 'tSpinMini': 2, 'allClear': 40, 'b2b': 1.3, 'combo': 1, 'tooHigh': -10, 'gap': -600, 'spikiness' : -80}
# b2b could have exponential impact on fitness (multiplier ^ b2b)

defaultbag = [Tetromino.I, Tetromino.J, Tetromino.L, Tetromino.O, Tetromino.S, Tetromino.T, Tetromino.Z]
randombag = []
bags1k = []
cnt = 0

for i in range(1000):
    shuffle(defaultbag)
    bags1k.extend(deepcopy(defaultbag))

class Node: 
    def __init__(self, position: Vector2Int, rotation: int, path: list, ):
        self.position = position
        self.rotation = rotation
        self.path = path

    def __str__(self):
        return f"Position: {self.position}, Rotation: {self.rotation}, Path: {self.path}"

    def __repr__(self):
        return f"Position: {self.position}, Rotation: {self.rotation}, Path: {self.path}"

class Placement:
    def __init__(self, position: Vector2Int, rotation: int, path: list, linesCleared: int, tSpin: bool, tSpinMini: bool):
        self.position = position
        self.rotation = rotation
        self.path = path
        self.linesCleared = linesCleared
        self.tSpin = tSpin
        self.tSpinMini = tSpinMini

    def __str__(self):
        return f"Position: {self.position}, Rotation: {self.rotation}, Path: {self.path}"

    def __repr__(self):
        return f"Position: {self.position}, Rotation: {self.rotation}, Path: {self.path}"

class BoardWithPiece:
    # size 10 x 40
    # has piece
    def __init__(self, piece: Piece = Piece(choice(list(Tetromino))), cells = None):
        if cells is not None:
            self.cells = cells
        else:
            self.cells = [[0 for x in range(10)] for y in range(40)]
        self.piece = piece

    def __str__(self):
        # should be upside down
        output = ""
        for y in range(19, -1, -1):
            for x in range(10):
                if(str(self.cells[y][x]) == "0"):
                    output += "_"
                elif(str(self.cells[y][x]) == "1"):
                    output += "*"
                else:
                    output += "X"
            output += "\n"
        return output
    
    def __repr__(self):
        # should be upside down
        output = ""
        for y in range(39, -1, -1):
            for x in range(10):
                if(str(self.cells[y][x]) == "0"):
                    output += "_"
                elif(str(self.cells[y][x]) == "1"):
                    output += "*"
                else:
                    output += "X"
            output += "\n"
        return output
    
    def isValid(self, position: Vector2Int, rotation: int):
        # check if piece is in bounds
        for cell in Cells[self.piece.tetromino][rotation]:
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
                queue.append(Node(position - Vector2Int(0, 1), rotation, path + [("S", Vector2Int(0, 0))]))

            # left 
            if self.isValid(position - Vector2Int(1, 0), rotation):
                queue.append(Node(position - Vector2Int(1, 0), rotation, path + [("L", Vector2Int(0, 0))]))
            
            # right
            if self.isValid(position + Vector2Int(1, 0), rotation):
                queue.append(Node(position + Vector2Int(1, 0), rotation, path + [("R", Vector2Int(0, 0))]))

            # rotate clockwise
            newrotation = (rotation + 1) % 4

            newCells = Cells[self.piece.tetromino][newrotation]

            offsetList = []

            if self.piece == Tetromino.I:
                offsetList = WallKicksI[rotation]            
            else:
                offsetList = WallKicksJLOSTZ[rotation]

            for offset in offsetList:
                if self.isRotationValid(newCells, position + offset):
                    queue.append(Node(position + offset, newrotation, path + [("CW", offset)]))
                    break

            # rotate counterclockwise

            newrotation = (rotation - 1) % 4

            newCells = Cells[self.piece.tetromino][newrotation]

            offsetList = []

            if self.piece == Tetromino.I:
                offsetList = CounterWallKicksI[rotation]
            else:
                offsetList = CounterWallKicksJLOSTZ[rotation]

            for offset in offsetList:
                if self.isRotationValid(newCells, position + offset):
                    queue.append(Node(position + offset, newrotation, path + [("CCW", offset)]))
                    break

            # flip 180

            newrotation = (rotation + 2) % 4

            newCells = Cells[self.piece.tetromino][newrotation]

            offsetList = Flips[rotation]

            for offset in offsetList:
                if self.isRotationValid(newCells, position + offset):
                    queue.append(Node(position + offset, newrotation, path + [("180", offset)]))
                    break
        
        return finalPlacements
    

def nextState(board: BoardWithPiece, placement: Node):
    board = deepcopy(board)
    position, rotation = placement

    fitness = 0

    # set the piece
    for cell in Cells[board.piece.tetromino][rotation]:
        # if obsturcted, game over
        posx = position.x + cell.x
        posy = position.y + cell.y
        if board.cells[posy][posx] != 0:
            return board, -2147000000
        board.cells[posy][posx] = 1
    
     
    # get max height
    maxHeight = 0
    for y in range(39, -1, -1):
        if 1 in board.cells[y]:
            maxHeight = y
            break

    # calculate board spikiness (diff between heights of adiacent columns)
    spikiness = 0
    forgiveOneWell = True
    # get heights of first column
    height1 = 0
    height2 = 0
    for y in range(39, -1, -1):
        if board.cells[y][0] == 1:
            height1 = y
            break
    
    for x in range(1, 10):
        for y in range(39, -1, -1):
            if board.cells[y][x] == 1:
                height2 = y
                break
        if abs(height1 - height2) > 2:
            if forgiveOneWell:
                forgiveOneWell = False
            else:
                spikiness += abs(height1 - height2)
        height1 = height2

    fitness += fitnessMultipliers['spikiness'] * spikiness
    if maxHeight > 11:
        fitness += fitnessMultipliers['tooHigh']
    
    # game over from height
    if maxHeight > 23:
        return board, -2147000000

    # check for cleared lines
    cntlines = 0
    for y in range(maxHeight, -1, -1):
        # print(board.cells[y])
        if 0 not in board.cells[y]:
            # clear line
            board.cells.pop(y)
            board.cells.insert(38, [0 for x in range(10)])
            cntlines += 1

    # print(cntlines, "lines cleared")

    fitness += fitnessMultipliers['linesCleared'][cntlines]

    
    # check for all clear
    if 1 not in board.cells[0]:
        fitness += fitnessMultipliers['allClear']

    # check if t spin or t spin mini

    # get gaps
    gaps = 0
    
    # if a well is covered, add a point to gaps for each cell in the well

    for x in range(10):
        for y in range(40):
            if board.cells[y][x] == 1:
                # go down until you hit a 1
                for y2 in range(y - 1, -1, -1):
                    if board.cells[y2][x] == 0:
                        gaps += 1
                    else:
                        break

    fitness += fitnessMultipliers['gap'] * gaps

    # b2b and combo

    board.piece = Piece(bags1k[cnt])
    return board, fitness

def displayPath(board1: BoardWithPiece, path: list):
    board = deepcopy(board1)

    print(path)

    for cell in Cells[board.piece.tetromino][board.piece.rotation]:
            posx = board.piece.position.x + cell.x
            posy = board.piece.position.y + cell.y
            board.cells[posy][posx] = 2
    print(board)
    for move, offset in path:
        # clear current piece from board
        for cell in Cells[board.piece.tetromino][board.piece.rotation]:
            posx = board.piece.position.x + cell.x
            posy = board.piece.position.y + cell.y
            board.cells[posy][posx] = 0
        # move piece
        if move == "S":
            board.piece = board.piece.moveDown()
        elif move == "L":
            board.piece = board.piece.moveLeft()
        elif move == "R":
            board.piece = board.piece.moveRight()
        elif move == "CW":
            board.piece = board.piece.rotateClockwise(offset)
        elif move == "CCW":
            board.piece = board.piece.rotateCounterClockwise(offset)
        elif move == "180":
            board.piece = board.piece.flip180(offset)
        # add piece to board
        for cell in Cells[board.piece.tetromino][board.piece.rotation]:
            posx = board.piece.position.x + cell.x
            posy = board.piece.position.y + cell.y
            board.cells[posy][posx] = 2
        print(board)



# piece = Piece(Tetromino.T)
# board = BoardWithPiece(piece)

# # line6 = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
# # line5 = [1, 1, 1, 0, 0, 0, 1, 1, 1, 1]
# # line4 = [1, 1, 1, 0, 0, 1, 1, 1, 1, 1]
# # line3 = [1, 1, 1, 0, 0, 0, 1, 1, 1, 1]
# # line2 = [1, 1, 1, 1, 1, 0, 1, 1, 1, 1]
# # line1 = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
# # line0 = [1, 1, 1, 1, 1, 0, 1, 1, 1, 1]
# # board.cells[0] = line0
# # board.cells[1] = line1
# # board.cells[2] = line2
# # board.cells[3] = line3
# # board.cells[4] = line4
# # board.cells[5] = line5
# # board.cells[6] = line6
# placements = board.findPlacementsAsDict()
# # print(sorted([i for i in placements.keys()], key = lambda x: [x[1], x[0].x, x[0].y]))

# displayPath(board, placements[((5, 1), 3)])

# board = nextState(board, ((5, 1), 3))
board = BoardWithPiece()
while True:
    cnt += 1
    placements = board.findPlacementsAsDict()
    print(board)
    bestplacement = None
    fitness = -2147000000
    for placement in placements.keys():
        nextboard, nextfitness = nextState(board, placement)
        if nextfitness >= fitness:
            fitness = nextfitness
            bestplacement = placement
    print(bestplacement)
    print(fitness)
    if fitness == -2147000000:
        break
    board, _ = nextState(board, bestplacement)
    

print(cnt)