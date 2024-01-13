from benchmark import *
from play1v1 import *
import json

base_path = 'graphing_weights/episode_'
start_episode_num = 50
end_episode_num = 4201
step = 50
max_pieces_per_run = 5000
multiplayer_games = 32
single_player_runs = 3
# dictionary of type episode_number: [avg_reward, avg_max_height, avg_piece_count, 1v1_wins]
scores = {}

for ep in range(start_episode_num, end_episode_num + 1, step):
  weights_path = f'{base_path}{ep}.hdf5'

  total_reward = 0
  total_max_height = 0
  total_piece_count = 0

  for _ in range(single_player_runs):
    reward, max_height, piece_count = get_agent_performance(weights_path, max_pieces_per_run)
    # add a penalty if it does not even manage to finish all pieces
    if piece_count < max_pieces_per_run: 
      reward -= 5

    total_reward += reward / piece_count
    total_max_height += max_height / piece_count
    total_piece_count += piece_count

  results_1v1 = play_1v1(weights_path, 'king.hdf5', multiplayer_games)
  wins_against_king = results_1v1.count("1")
  
  scores[ep] = [total_reward / single_player_runs, total_max_height / single_player_runs, total_piece_count / single_player_runs,wins_against_king]
  with open('scores.txt', 'a') as txt_file:
    txt_file.write(f"{ep}: {[total_reward / single_player_runs, total_max_height / single_player_runs, total_piece_count / single_player_runs,wins_against_king]}\n") 

with open('scores.json', 'w') as json_file:
  json.dump(scores, json_file)
