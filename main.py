'''This file plays the blackjack game. The user inputs what type of game play they want to see.'''
from players import Player

playerTypes = ['Baseline', 'Oracle']

def main():   
    while True:
        playerName = raw_input('What type of player do you want? (Baseline, Oracle) ')
        if playerName in playerTypes:
            player = Player(playerName)
            player.playGame()
            break

if __name__ == '__main__': main()
