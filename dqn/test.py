import unittest
from test_boards import *
from deep_q import *

class TestAgent(unittest.TestCase):

    def get_agent(self, weights_path='4025.hdf5'):
        agent = DQNAgent(play_mode=True)
        agent.model.load_weights(weights_path)
        return agent

    def test_l1(self):
        agent = self.get_agent()
        agent.state = GameState(Board(10, 40, l1), Piece.T, Piece.I, 0)

        predicted_board = agent.get_play_best_state(agent.state.generateChildren()).board.board
        expected_board = Board(10, 40, exp1).board
        
        self.assertEqual(predicted_board, expected_board)

    def test_l2(self):
        agent = self.get_agent()
        agent.state = GameState(Board(10, 40, l2), Piece.T, Piece.I, 0)

        predicted_board = agent.get_play_best_state(agent.state.generateChildren()).board.board
        expected_board = Board(10, 40, exp2).board
        
        self.assertEqual(predicted_board, expected_board)
        
    def test_l3(self):
        agent = self.get_agent()
        agent.state = GameState(Board(10, 40, l3), Piece.T, Piece.I, 0)

        predicted_board = agent.get_play_best_state(agent.state.generateChildren()).board.board
        expected_board = Board(10, 40, exp3).board
        
        self.assertEqual(predicted_board, expected_board)
        
    def test_l4(self):
        agent = self.get_agent()
        agent.state = GameState(Board(10, 40, l4), Piece.T, Piece.I, 0)

        predicted_board = agent.get_play_best_state(agent.state.generateChildren()).board.board
        expected_board = Board(10, 40, exp4).board
        
        self.assertEqual(predicted_board, expected_board)
    
    def test_l5(self):
        agent = self.get_agent()
        agent.state = GameState(Board(10, 40, l5), Piece.T, Piece.I, 0)

        predicted_board = agent.get_play_best_state(agent.state.generateChildren()).board.board
        expected_board = Board(10, 40, exp5).board
        
        self.assertEqual(predicted_board, expected_board)

    def test_l6(self):
        agent = self.get_agent()
        agent.state = GameState(Board(10, 40, l6), Piece.L, Piece.T, 0)

        predicted_board = agent.get_play_best_state(agent.state.generateChildren()).board.board
        expected_board = Board(10, 40, exp6).board
        
        self.assertEqual(predicted_board, expected_board)

    def test_l7(self):
        agent = self.get_agent()
        agent.state = GameState(Board(10, 40, l7), Piece.Z, Piece.T, 0)

        predicted_board = agent.get_play_best_state(agent.state.generateChildren()).board.board
        expected_board = Board(10, 40, exp7).board
        
        self.assertEqual(predicted_board, expected_board)


if __name__ == '__main__':
    unittest.main()
