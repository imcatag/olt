from deep_q import *
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

agent = DQNAgent(play_mode=True)

agent.play(weights_path='weightscpu/episode_350')
