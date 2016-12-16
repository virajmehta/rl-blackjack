'''
This file plays the blackjack game. The user inputs what type of game play they want to see.
'''
from players import Baseline, Oracle, RLPlayer

players = ['Baseline', 'Oracle', 'RL']
strategies = ['Hi-Lo', 'Omega II', 'Wong Halves']
algorithms = ['Q-Learning']

def getAlgorithm():
    while True:
        algorithm = raw_input('What algorithm should RL use? (Q-Learning) ')
        if algorithm in algorithms: return algorithm

def getStrategy():
    while True:
        strategy = raw_input('What counting strategy should RL use? (Hi-Lo, Omega II, Wong Halves) ')
        if strategy in strategies: return strategy

def main():
    player = RLPlayer('Hi-Lo', 'Q-Learning')
    player.train(1000000)

    '''while True:
        playerName = raw_input('What type of player do you want? (Baseline, Oracle, RL) ')
        if playerName in players:
            player = None
            if playerName == 'Baseline':
                player = Baseline(playerName)
                player.playGame()
            elif playerName == 'Oracle':
                player = Oracle(playerName)
                player.playGame()
            else:
                player = RLPlayer(getStrategy(), getAlgorithm())
                player.train(1000000)
            break'''

if __name__ == '__main__': main()
