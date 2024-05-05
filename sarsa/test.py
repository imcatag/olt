import unittest
from test_boards import *
from main import *
from env import *

with open('weights.txt', 'r') as file:
    lines = file.readlines()
weights = eval(lines[-1].strip())

class TestAgent(unittest.TestCase):
    def get_approx_Q(self, state: GameState, weights) -> float:
      env = Env()
      features = env.normalize_features(state.features)
      return sum([weights[i] * features[i] for i in range(len(weights))])

    def get_next_state(self, state: GameState) -> GameState:
        next_possible_states = state.generateChildren()

        if len(next_possible_states) == 0:
            return

        return max(next_possible_states, key=lambda x: self.get_approx_Q(x, weights))

    def test_l1(self):
        state = GameState(Board(10, 40, l1), Piece.T, Piece.I, 0)

        predicted_board = self.get_next_state(state).board.board
        expected_board = Board(10, 40, exp1).board
        
        self.assertEqual(predicted_board, expected_board)

    def test_l2(self):
        state = GameState(Board(10, 40, l2), Piece.T, Piece.I, 0)

        predicted_board = self.get_next_state(state).board.board
        expected_board = Board(10, 40, exp2).board
        
        self.assertEqual(predicted_board, expected_board)
        
    def test_l3(self):
        state = GameState(Board(10, 40, l3), Piece.T, Piece.I, 0)

        predicted_board = self.get_next_state(state).board.board
        expected_board = Board(10, 40, exp3).board
        
        self.assertEqual(predicted_board, expected_board)
        
    def test_l4(self):
        state = GameState(Board(10, 40, l4), Piece.T, Piece.I, 0)

        predicted_board = self.get_next_state(state).board.board
        expected_board = Board(10, 40, exp4).board
        
        self.assertEqual(predicted_board, expected_board)
    
    def test_l5(self):
        state = GameState(Board(10, 40, l5), Piece.T, Piece.I, 0)

        predicted_board = self.get_next_state(state).board.board
        expected_board = Board(10, 40, exp5).board
        
        self.assertEqual(predicted_board, expected_board)

    def test_l6(self):
        state = GameState(Board(10, 40, l6), Piece.L, Piece.T, 0)

        predicted_board = self.get_next_state(state).board.board
        expected_board = Board(10, 40, exp6).board
        
        self.assertEqual(predicted_board, expected_board)

    def test_l7(self):
        state = GameState(Board(10, 40, l7), Piece.Z, Piece.T, 0)

        predicted_board = self.get_next_state(state).board.board
        expected_board = Board(10, 40, exp7).board
        
        self.assertEqual(predicted_board, expected_board)

    def test_l8(self):
        state = GameState(Board(10, 40, l8), Piece.Z, Piece.I, 0)

        predicted_board = self.get_next_state(state).board.board
        expected_board = Board(10, 40, exp8).board
        
        self.assertEqual(predicted_board, expected_board)

    def test_l9(self):
        state = GameState(Board(10, 40, l9), Piece.O, Piece.I, 0)

        predicted_board = self.get_next_state(state).board.board
        expected_board = Board(10, 40, exp9).board
        
        self.assertEqual(predicted_board, expected_board)

    def test_l10(self):
        state = GameState(Board(10, 40, l10), Piece.O, Piece.I, 0)

        predicted_board = self.get_next_state(state).board.board
        expected_board = Board(10, 40, exp10).board
        
        self.assertEqual(predicted_board, expected_board)
        

if __name__ == '__main__':
    unittest.main()
