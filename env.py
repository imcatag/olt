import random
from main import *


def min_max_scaling(x, x_min, x_max, new_min=0, new_max=1):
    return ((x - x_min) / (x_max - x_min)) * (new_max - new_min) + new_min


class Env:
    def __init__(self):
        self.board = Board()
        self.state = GameState(self.board, pieceQueue[0])
        # linesCleared, spikiness, covered, maxHeight, perfectClear, tspin, tspinmini
        self.weights = [0.1 for _ in range(11)]
        self.alpha = 0.5
        self.epsilon = 0.05

    # approximating Q by the estimate of the state I end up in
    def get_approx_Q(self, state: GameState) -> float:
        features = self.normalize_features(state.features)
        return sum([self.weights[i] * features[i] for i in range(len(self.weights))])

    # linesCleared 0, 1, 2, 3, 4, perfectClear, maxHeight, spikiness, covered, gaps, overHalf
    def normalize_features(self, features: List[float]) -> List[float]:
        normalized_features = deepcopy(features)

        normalized_features[0] = 0 if not normalized_features[0] else 1
        for i in range(6, 11):
            normalized_features[i] = min_max_scaling(normalized_features[i], 0, 20)
        return normalized_features

    def epsilon_greedy(self, next_states: List["GameState"]) -> GameState:
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(next_states)
        return max(next_states, key=lambda x: self.get_approx_Q(x))

    def update_weights(self, delta: float, features):
        self.weights = [
            self.weights[i] + self.alpha * delta * features[i]
            for i in range(len(self.weights))
        ]

    def train(self, num_episodes=10, gamma=0.7):
        for _ in range(num_episodes):
            self.state = GameState(self.board, pieceQueue[self.state.pieceCount + 1])
            print(self.weights)
            second_next_possible_states = None

            while True:
                # print(self.state)
                possible_next_states = (
                    second_next_possible_states
                    if second_next_possible_states != None
                    else self.state.generateChildren()
                )
                next_state = self.epsilon_greedy(possible_next_states)
                reward = next_state.evaluation
                features = self.normalize_features(next_state.features)

                second_next_possible_states = next_state.generateChildren()
                # check if next_state is terminal
                if len(second_next_possible_states) == 0:
                    self.update_weights(
                        reward - self.get_approx_Q(next_state), features
                    )
                    break

                second_next_state = self.epsilon_greedy(second_next_possible_states)
                self.update_weights(
                    reward
                    + gamma * self.get_approx_Q(second_next_state)
                    - self.get_approx_Q(next_state),
                    features,
                )

                self.state = deepcopy(next_state)
