from benchmark import *
# from play1v1 import *
import json

with open('new_weights.txt', 'r') as file:
  lines = file.readlines()
all_weights = [eval(line.strip()) for line in lines]

  
max_pieces_per_run = 100
multiplayer_games = 3
# dictionary of type episode_number: [avg_reward, avg_max_height, 1v1_wins]
scores = {}

for (i, weights) in enumerate(all_weights):
  reward, max_height, piece_count = get_agent_performance(weights, max_pieces_per_run)
  # add a penalty if it does not even manage to finish all pieces
  if piece_count < max_pieces_per_run: 
    reward -= 5

  # results_1v1 = play_1v1(weights_path, 'king.hdf5', multiplayer_games)
  # wins_against_king = results_1v1.count("1")
  
  scores[i] = [reward / piece_count, max_height / piece_count] #, wins_against_king]

with open('scores.json', 'w') as json_file:
  json.dump(scores, json_file)
