import unittest
from main import *
from deep_q import *

class TestAgent(unittest.TestCase):

    def test_l1(self):
        agent = DQNAgent(play_mode=True)
        agent.model.load_weights('good_weights_500_ep.hdf5')
        agent.state = GameState(Board(10, 40, l1), Piece.T, Piece.I, 0)

        predicted_state = agent.get_best_state(agent.state.generateChildren())
        
        self.assertEqual(predicted_state.board.board, expected_board)

    def test_l2(self):
        agent = DQNAgent(play_mode=True)
        agent.model.load_weights('good_weights_500_ep.hdf5')
        agent.state = GameState(Board(10, 40, l2), Piece.T, Piece.I, 0)

        predicted_state = agent.get_best_state(agent.state.generateChildren())
        
        self.assertEqual(predicted_state.board.board, expected_board)
        
    def test_l3(self):
        agent = DQNAgent(play_mode=True)
        agent.model.load_weights('good_weights_500_ep.hdf5')
        agent.state = GameState(Board(10, 40, l3), Piece.T, Piece.I, 0)

        predicted_state = agent.get_best_state(agent.state.generateChildren())
        
        self.assertEqual(predicted_state.board.board, expected_board)
        
    def test_l4(self):
        agent = DQNAgent(play_mode=True)
        agent.model.load_weights('good_weights_500_ep.hdf5')
        agent.state = GameState(Board(10, 40, l4), Piece.T, Piece.I, 0)

        predicted_state = agent.get_best_state(agent.state.generateChildren())
        
        self.assertEqual(predicted_state.board.board, expected_board)
    
    def test_l5(self):
        agent = DQNAgent(play_mode=True)
        agent.model.load_weights('good_weights_500_ep.hdf5')
        agent.state = GameState(Board(10, 40, l5), Piece.T, Piece.I, 0)

        predicted_state = agent.get_best_state(agent.state.generateChildren())
        
        self.assertEqual(predicted_state.board.board, expected_board)

    def test_l6(self):
        agent = DQNAgent(play_mode=True)
        agent.model.load_weights('good_weights_500_ep.hdf5')
        agent.state = GameState(Board(10, 40, l6), Piece.L, Piece.T, 0)

        predicted_state = agent.get_best_state(agent.state.generateChildren())
        
        self.assertEqual(predicted_state.board.board, expected_board)

    def test_l7(self):
        agent = DQNAgent(play_mode=True)
        agent.model.load_weights('good_weights_500_ep.hdf5')
        agent.state = GameState(Board(10, 40, l7), Piece.Z, Piece.T, 0)

        predicted_state = agent.get_best_state(agent.state.generateChildren())
        
        self.assertEqual(predicted_state.board.board, expected_board)
        



if __name__ == '__main__':
    unittest.main()
