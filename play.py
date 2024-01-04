from deep_q import *

agent = DQNAgent(play_mode=True)

agent.play(weights_path='weights/episode_450')
