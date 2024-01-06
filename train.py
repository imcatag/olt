from deep_q import *

agent = DQNAgent(model_name= 'unsafe_good.hdf5')

agent.train(3000)
