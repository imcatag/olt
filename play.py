from time import sleep
from main import *
from env import *

with open('new_file.txt', 'r') as file:
    lines = file.readlines()
weights = eval(lines[-1].strip())


env = Env()
pieceQueue = []
for i in range(10000):
    shuffle(defaultbag)
    pieceQueue += defaultbag

board = Board()
state = GameState(board, pieceQueue[0])


def get_approx_Q(state: GameState, weights) -> float:
        features = env.normalize_features(state.features)
        return sum([weights[i] * features[i] for i in range(len(weights))])


while True:
    next_possible_states = state.generateChildren()

    if len(next_possible_states) == 0:
        break

    next_state = max(next_possible_states, key=lambda x: get_approx_Q(x, weights))
    reward = next_state.evaluation

    print(state)
    state = deepcopy(next_state)
    # sleep(0.6)
