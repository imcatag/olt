import random
import numpy as np
from main import *
from helper import *


# we need the next piece from c# in order to generate the next boards..
class GameImageState:
    # takes a 21 * 15 game state and pads it to make it square
    def __init__(
        self,
        actual_state: List[List[int]],
        piece: Piece,
        held_piece: Piece,
        next_bag_piece: Piece,
    ):
        self.repr = np.pad(
            actual_state, ((0, 0), (0, 6)), mode="constant", constant_values=0
        )
        self.game_state = self.get_game_state(actual_state)
        self.piece = piece
        self.held_piece = held_piece
        self.next_bag_piece = next_bag_piece

    def get_game_state(self, actual_state: List[List[int]]) -> GameState:
        board = Board(board=np.array(actual_state)[-20:, :10])
        return GameState(board, self.piece)

    # TODO: implement this
    def get_actual_state(self, game_state: GameState):
        return []

    def generate_children(self):
        return [self.get_actual_state(x) for x in self.game_state.generateChildren()]


class DQNAgent:
    def __init__(self, state_size=21 * 21):
        self.lr = 0.001
        self.gamma = 0.95
        self.exploration_prob = 1.0
        self.exploration_prob_decay = 0.005
        self.batch_size = 32
        self.total_steps = 0

        # a list of dictionaries that store (s_t, a_t, r_t, s_t+1)
        self.memory_buffer = list()
        self.max_memory_buffer = 2000

        # Define a model that returns the expected value of the given state + action
        self.model = Sequential(
            [
                Dense(units=24, input_dim=state_size, activation="relu"),
                Dense(units=24, activation="relu"),
                Dense(units=action_size, activation="linear"),
            ]
        )
        self.model.compile(
            loss="mse", optimizer=Adam(lr=self.lr)
        )  # RMSProp could be another choice here

    def get_approx_Q(state: GameImageState) -> float:
        # add img std? https://www.tensorflow.org/api_docs/python/tf/image/per_image_standardization
        return self.model.predict(state.repr)

    def get_next_state(self, next_states: List["GameImageState"]) -> GameImageState:
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(next_states)
        return max(next_states, key=lambda x: self.get_approx_Q(x))

    def update_exploration_probability(self):
        self.exploration_prob = self.exploration_prob * np.exp(
            -self.exploration_prob_decay
        )

    def store_episode(self, current_state, reward, next_state, terminated):
        # current_state is actually the current state-action pair
        self.memory_buffer.append(
            {
                "current_state": current_state,
                "reward": reward,
                "next_state": next_state,
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
            current_q = self.get_approx_Q(experience["current_state"])
            target_q = experience["reward"]
            if not experience["terminated"]:
                target_q += self.gamma * self.model.predict(experience["next_state"])

            training_data.append(experience["current_state"])
            training_labels.append(target_q - current_q)

        self.model.fit(np.array(training_data), np.array(training_labels))

    def train(self, n_episodes=10):
        for _ in range(n_episodes):
            current_state = [] # get the current state 

            while True:
                next_possible_states = current_state.generate_children()
                next_state = self.get_next_state(next_possible_states)
                reward = 0 # compute reward here

                terminated = len(next_possible_states) == 0

                self.store_episode(current_state, reward, next_state, terminated) 

                if terminated:
                    self.update_exploration_probability()
                    break
                
                current_state = next_state

            if self.total_steps >= self.batch_size:
                self.train_episode()

        self.model.save_weights('recent_weights.hdf5')
