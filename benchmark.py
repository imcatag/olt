from main import *
from env import *
import time

env = Env()

def get_approx_Q(state: GameState, weights) -> float:
    features = env.normalize_features(state.features)
    return sum([weights[i] * features[i] for i in range(len(weights))])


with open('new_file.txt', 'r') as file:
    lines = file.readlines()
last_weights = eval(lines[-1].strip())


total_piece_count = 0
total_reward = 0
total_max_heights = 0
no_different_runs = 1
pieces_per_run = 100

# returns total reward, total max height, and total piece count over the entire game
def get_agent_performance(weights: List[float], max_pieces_per_run: int):
    pieceQueue = []
    for i in range(2000):
        shuffle(defaultbag)
        pieceQueue += defaultbag
    board = Board()
    state = GameState(board, pieceQueue[0])

    piece_count = 0
    reward = 0
    max_height = 0

    while piece_count < max_pieces_per_run:
        next_possible_states = state.generateChildren()

        if len(next_possible_states) == 0:
            break

        next_state = max(next_possible_states, key=lambda x: get_approx_Q(x, weights))

        reward += next_state.evaluation
        max_height += next_state.features[3]

        print(state)
        piece_count += 1
        state = deepcopy(next_state)

    return reward, max_height, piece_count


# for _ in range(no_different_runs):
#     reward, max_height, piece_count = get_agent_performance(last_weights, pieces_per_run)
#     total_reward += reward
#     total_max_heights += max_height
#     total_piece_count += piece_count

#     print(f'Got an average reward of {reward / piece_count}')
#     print(f'Got an average max height of {max_height / piece_count}')
#     time.sleep(1)

# print(f'Average reward over {no_different_runs} runs of {pieces_per_run} pieces: {total_reward / total_piece_count}')
# print(f'Average max height over {no_different_runs} runs of {pieces_per_run} pieces: {total_max_heights / total_piece_count}')
