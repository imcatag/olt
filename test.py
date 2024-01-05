import unittest
from test_boards import *
from deep_q import *
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class TestAgent(unittest.TestCase):

    def get_agent(self, weights_path='weights/episode_950.hdf5'):
        agent = DQNAgent(play_mode=True)
        agent.model.load_weights(weights_path)
        return agent

    def test_l1(self):
        agent = self.get_agent()
        agent.state = GameState(Board(10, 40, l1), Piece.T, Piece.I, 0)

       # get 3 best states
        next_states = agent.state.generateChildren()
        next_states_input_data = np.array([agent.get_model_input_from_repr(next_state.get_game_repr()) for next_state in next_states])
        next_states_input_data = next_states_input_data.reshape((len(next_states_input_data), 20, 20, 1))
        predictions = agent.model.predict_on_batch(next_states_input_data)
        next_states = sorted(zip(next_states, predictions), key=lambda x: x[1], reverse=True)[:3]

        print(next_states)
        for i, s in enumerate(next_states):
            # print board and evaluation
            print(*s[0].get_game_repr(), sep='\n')
            print(s[0].features)
            print(s[0].evaluation, next_states[i][1])
            print()

        
        next_states = [x[0] for x in next_states]

        predicted_board = agent.get_play_best_state(next_states).board.board

        print(*predicted_board, sep='\n')

        expected_board = Board(10, 40, exp1).board
        
        self.assertEqual(predicted_board, expected_board)

    def test_l2(self):
        agent = self.get_agent()
        agent.state = GameState(Board(10, 40, l2), Piece.T, Piece.I, 0)

        # get 3 best states
        next_states = agent.state.generateChildren()
        next_states_input_data = np.array([agent.get_model_input_from_repr(next_state.get_game_repr()) for next_state in next_states])
        next_states_input_data = next_states_input_data.reshape((len(next_states_input_data), 20, 20, 1))
        predictions = agent.model.predict_on_batch(next_states_input_data)
        next_states = sorted(zip(next_states, predictions), key=lambda x: x[1], reverse=True)[:3]

        print()
        for i, s in enumerate(next_states):
            # print board and evaluation
            print(*s[0].get_game_repr(), sep='\n')
            print(s[0].evaluation, next_states[i][1])
            print()

        next_states = [x[0] for x in next_states]

        predicted_board = agent.get_play_best_state(next_states).board.board

        print(*predicted_board, sep='\n')
        expected_board = Board(10, 40, exp2).board
        
        self.assertEqual(predicted_board, expected_board)
        
    def test_l3(self):
        agent = self.get_agent()
        agent.state = GameState(Board(10, 40, l3), Piece.T, Piece.I, 0)

        # get 3 best states
        next_states = agent.state.generateChildren()
        next_states_input_data = np.array([agent.get_model_input_from_repr(next_state.get_game_repr()) for next_state in next_states])
        next_states_input_data = next_states_input_data.reshape((len(next_states_input_data), 20, 20, 1))
        predictions = agent.model.predict_on_batch(next_states_input_data)
        next_states = sorted(zip(next_states, predictions), key=lambda x: x[1], reverse=True)[:3]

        print()
        for i, s in enumerate(next_states):
            # print board and evaluation
            print(*s[0].get_game_repr(), sep='\n')
            print(s[0].evaluation, next_states[i][1])
            print()

        next_states = [x[0] for x in next_states]

        predicted_board = agent.get_play_best_state(next_states).board.board

        print(*predicted_board, sep='\n')
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
