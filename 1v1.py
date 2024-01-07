from deep_q import *
import os
from random import randint
from side_by_side import print_side_by_side
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

a1wins = 0
a2wins = 0
results = ""
for _ in range(32):
    pieceQueue = []
    for _ in range(30000):
        shuffle(defaultbag)
        pieceQueue += defaultbag
    
    agent1 = DQNAgent(play_mode=True, model_name='4025.hdf5')
    agent2 = DQNAgent(play_mode=True, model_name='4200.hdf5')

    agent1.state = GameState(Board(), pieceQueue[0])
    agent2.state = GameState(Board(), pieceQueue[0])

    def getNextState(agent):
        next_possible_states = agent.state.generateChildren()

        if len(next_possible_states) == 0:
            return False

        next_state = agent.get_play_best_state(next_possible_states)

        return next_state

    toAddto1 = []
    toAddto2 = []
    totalCleared1 = 0
    totalCleared2 = 0
    totalSent1 = 0
    totalSent2 = 0


    while(True):
        # do threads to get next state for each agent
        next_state1 = getNextState(agent1)
        next_state2 = getNextState(agent2)

        if next_state1 == False and next_state2 == False:
            results += "T"
            print('Tie!')
            break
        if next_state1 == False:
            results += "2"
            print('Agent 2 wins!')
            break
        elif next_state2 == False:
            results += "1"
            print('Agent 1 wins!')
            break

        lines1s = next_state1.sending
        lines2s = next_state2.sending
        lines1c = next_state1.clearing
        lines2c = next_state2.clearing

        totalCleared1 += lines1c
        totalCleared2 += lines2c
        totalSent1 += lines1s
        totalSent2 += lines2s

        sends = lines1s - lines2s

        if sends > 0:
            toAddto2.append(sends)
        elif sends < 0:
            toAddto1.append(-sends)

        if len(toAddto1) > 0 and lines1c == 0:
            # send up to 8 lines
            sendable = 8
            while sendable > 0 and len(toAddto1) > 0:
                lines = min(sendable, toAddto1[0])
                # add garbage to agent 2
                next_state1.board.addGarbage(lines)
                toAddto1[0] -= lines
                sendable -= lines
                if toAddto1[0] == 0:
                    toAddto1.pop(0)
        
        if len(toAddto2) > 0 and lines2c == 0:
            # send up to 8 lines
            sendable = 8
            while sendable > 0 and len(toAddto2) > 0:
                lines = min(sendable, toAddto2[0])
                # add garbage to agent 1
                next_state2.board.addGarbage(lines)
                toAddto2[0] -= lines
                sendable -= lines
                if toAddto2[0] == 0:
                    toAddto2.pop(0)        
        print_side_by_side(str(lines1s), str(lines2s))
        print_side_by_side(str(lines1c), str(lines2c))
        print_side_by_side(str(next_state1), str(next_state2))

        agent1.state = deepcopy(next_state1)
        agent2.state = deepcopy(next_state2)

    print(f'Agent 1 sent {totalSent1} lines and cleared {totalCleared1} lines')
    print(f'Agent 2 sent {totalSent2} lines and cleared {totalCleared2} lines')

print(results)
print(f'Agent 1 won {results.count("1")} times')
print(f'Agent 2 won {results.count("2")} times')