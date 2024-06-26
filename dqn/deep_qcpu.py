import random
import numpy as np
from main import *
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten


class DQNAgent:
    def __init__(self, input_shape = (20, 20, 1), play_mode=False):
        self.empty_board = Board()
        self.state = GameState(self.empty_board, pieceQueue[0])
        self.lr = 0.001
        self.gamma = 0.95
        self.exploration_prob = 1.0
        self.exploration_prob_decay = 0.005
        self.min_exploration_prob = 0.05
        self.batch_size = 32
        self.total_steps = 0
        self.play_mode = play_mode
        self.total_pieces_placed = 0

        # a list of dictionaries that store (s_t, a_t, r_t, s_t+1)
        self.memory_buffer = list()
        self.max_memory_buffer = 2000

        # Define a model that returns the expected value of the given state + action
        self.model = Sequential([
            Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=input_shape),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(64, kernel_size=(3, 3), activation='relu'),
            MaxPooling2D(pool_size=(2, 2)),
            Flatten(),
            Dense(128, activation='relu'),
            Dense(1, activation='linear') 
        ])

        if not self.play_mode:
            self.model.summary()

        self.model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])  # RMSProp could be another choice here

    def get_model_input_from_repr(self, state_repr: List[List[int]]):
        return np.array(state_repr).reshape(-1, 20, 20, 1)

    # game_state_repr = the 20x20 board
    def get_approx_Q(self, game_state_repr: List[List[int]]) -> float:
        # add img std? https://www.tensorflow.org/api_docs/python/tf/image/per_image_standardization]
        input_data = self.get_model_input_from_repr(game_state_repr)
        return self.model(input_data)

    def get_next_state(self, next_states: List["GameState"]) -> GameState:
        if random.uniform(0, 1) < self.exploration_prob:
            return random.choice(next_states)
        return max(next_states, key=lambda x: self.get_approx_Q(x.get_game_repr()))

    def update_exploration_probability(self):
        self.exploration_prob = max(self.exploration_prob * np.exp(
            -self.exploration_prob_decay
        ), self.min_exploration_prob)

    def store_episode(self, current_state, reward, next_state, terminated):
        # current_state is actually the current state-action pair
        self.memory_buffer.append(
            {
                "current_state_board": current_state.get_game_repr(), # "board" is actually game state repr
                "reward": reward,
                "next_state_board": next_state.get_game_repr(),
                "terminated": terminated,
            }
        )

        if len(self.memory_buffer) > self.max_memory_buffer:
            self.memory_buffer.pop(0)

    def train_episode(self):
        batch = np.random.choice(self.memory_buffer, self.batch_size)
        training_data = []
        training_labels = []

        for experience in batch:
            current_q = self.get_approx_Q(experience["current_state_board"])
            q_target = experience["reward"]
            if not experience["terminated"]:
                next_q = self.get_approx_Q(experience["next_state_board"])
                q_target += self.gamma * next_q

            training_data.append(experience["current_state_board"])
            training_labels.append(q_target - current_q)

        self.model.fit(np.array(training_data), np.array(training_labels))

    def train(self, n_episodes=10):
        for ep in range(1, n_episodes + 1):
            print('<------------------------------->')
            print('episode: ', ep)
            print('exploration rate: ', self.exploration_prob)
            print('Total pieces placed: ', self.total_pieces_placed)
            print('<------------------------------->')
            print('playing...')
            self.state = GameState(self.empty_board, pieceQueue[self.state.pieceCount + 1])

            while True:
                next_possible_states = self.state.generateChildren()
                terminated = len(next_possible_states) == 0

                if terminated:
                    self.update_exploration_probability()
                    break
                
                next_state = self.get_next_state(next_possible_states)
                self.total_pieces_placed += 1
                reward = next_state.evaluation # not the best reward

                self.total_steps += 1
                self.store_episode(self.state, reward, next_state, terminated) 
                
                self.state = deepcopy(next_state)

            if self.total_steps >= self.batch_size:
                print('training...')
                self.train_episode()
            
            if ep != 0 and ep % 50 == 0:
                self.model.save_weights(f'weightscpu/episode_{ep}.hdf5')

        self.model.save_weights('recent_weightscpu.hdf5')

    def play(self, weights_path='recent_weightscpu'):
        self.model.load_weights(f'{weights_path}.hdf5')
        pieceQueue = []
        for _ in range(10000):
            shuffle(defaultbag)
            pieceQueue += defaultbag

        board = Board()
        state = GameState(board, pieceQueue[0])

        while True:
            next_possible_states = state.generateChildren()

            if len(next_possible_states) == 0:
                break

            next_state = max(next_possible_states, key=lambda x: self.get_approx_Q(x.get_game_repr()))
            print(state)
            state = deepcopy(next_state)
