from deep_qcpu import *
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
agent = DQNAgent()

agent.train(500)
