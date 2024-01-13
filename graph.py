from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import json

with open('scores.json', 'r') as json_file:
  scores = json.load(json_file)

episode_numbers = list(scores.keys())
avg_rewards = [score[0] for score in scores.values()]
avg_max_heights = [score[1] for score in scores.values()]
avg_piece_counts = [score[2] / 1000 for score in scores.values()]
scores_1v1 = [score[3] for score in scores.values()]

plt.figure(figsize=(10, 6))
plt.plot(episode_numbers, avg_rewards, label='Average Reward', marker='o')
plt.plot(episode_numbers, avg_max_heights, label='Average Max Height', marker='o')
plt.plot(episode_numbers, avg_piece_counts, label='Average Piece Counts (/ 1000)', marker='o')
plt.plot(episode_numbers, scores_1v1, label='Wins against best agent', marker='o')
plt.xlabel('Episode Number')
plt.ylabel('Value')
plt.title('Improvements Over Time')
plt.legend()
plt.show()
