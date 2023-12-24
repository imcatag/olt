import random
from main import *


def min_max_scaling(x, x_min, x_max, new_min=0, new_max=1):
    return ((x - x_min) / (x_max - x_min)) * (new_max - new_min) + new_min


class Env:
    def __init__(self):
        self.board = Board()
        self.state = GameState(self.board, pieceQueue[0])
        # linesCleared, spikiness, covered, maxHeight, perfectClear, tspin, tspinmini
        self.weights = [0.1 for _ in range(7)]
        self.alpha = 0.5
        self.epsilon = 0.05

    def step(self):
        # pick an action at random
        possible_next_states = self.state.generateChildren()
        next_state = random.choice(possible_next_states)
        return next_state

    # approximating Q by the estimate of the state I end up in
    def get_approx_Q(self, board: Board, action: Placement) -> float:
        _, _, new_state_features = PlacePieceAndEvaluate(board, action)
        return sum(
            [self.weights[i] * new_state_features[i] for i in range(len(self.weights))]
        )

    # linesCleared, spikiness, covered, maxHeight, perfectClear, tspin, tspinmini
    def normalize_features(self, features: List[float])->List[float]:
        normalized_features = deepcopy(features)
        
        normalized_features[0] = min_max_scaling(normalized_features[0], 0, 5)
        normalized_features[1] = -min_max_scaling(normalized_features[1], 0, 20)
        normalized_features[2] = -min_max_scaling(normalized_features[2], 0, 20)
        normalized_features[3] = -min_max_scaling(normalized_features[3], 0, 20)
        normalized_features[4] = 1 if normalized_features[4] else 0
        # tspin and tspin mini not normalized 

        return normalized_features
        
    def epsilon_greedy(
        self, board: Board, possible_actions: List[Placement]
    ) -> Placement:
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(possible_actions)
        return max(possible_actions, key=lambda x: self.get_approx_Q(board, x))

    def train(self, num_episodes=10, gamma=0.5):
        possible_actions = self.state.board.findPlacements(self.state.piece)
        action = self.epsilon_greedy(self.state.board, possible_actions)
        new_board, reward, new_state_features = PlacePieceAndEvaluate(
            self.state.board, action
        )

        for _ in range(num_episodes):
            old_board = deepcopy(self.state.board)
            self.state.board = deepcopy(new_board)
            self.state.pieceCount += 1
            new_possible_actions = self.state.board.findPlacements(
                pieceQueue[self.state.pieceCount]
            )

            if len(new_possible_actions) == 0:
                # terminal state case
                pass

            # choose new action
            new_action = self.epsilon_greedy(self.state.board, new_possible_actions)
            new_board, _, _ = PlacePieceAndEvaluate(self.state.board, new_action)

            self.weights = [
                self.weights[i]
                + self.alpha
                * (
                    reward
                    + gamma * self.get_approx_Q(new_board, new_action)
                    - self.get_approx_Q(old_board, action)
                )
                * new_state_features[i]
                for i in range(len(self.weights))
            ]

            action = new_action
            print(self.weights)


env = Env()

env.train()
