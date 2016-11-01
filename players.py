'''
This is the file containing all the code needed for each type of blackjack player. 
It will eventually contain six player types: Dealer, Baseline, Oracle, Hi-Lo, Omega II, 
and Wong Halves. It currently contains the implementations for the first three.
''' 
from simulator import Game

class Player():
    '''
    This is the class that wraps over the functions shared by each of the types of players.
    '''
    def __init__(self, playerName):
        self.game = Game()
        self.player = None
        self.playerName = playerName
        self.dealer = Dealer(self.game)
        self.winnings = 0
        if (playerName == 'Baseline'):
            self.player = Baseline(self.game)
        if (playerName == 'Oracle'):
            self.player = Oracle(self.game)
    
    def playGame(self):
        '''
        Plays desired number of hands for given number of iterations.
        '''
        for _ in range(100):
            self.player.hand, self.player.total = self.game.startHand(1)
            print '%s\'s Turn!\n' % self.playerName
            print 'Hand: %s' % self.player.hand
            print 'Total: %s' % self.player.total
            self.player.playHand()
            self.dealer.playHand()
            self.getWinnings()
        print 'Total Winnings: %s' % self.winnings

    def getWinnings(self):
        '''
        Calls getReward() from Game to retrieve the outcome of the hand. 
        Updates total winnings over the whole game.
        '''
        result = self.game.getReward()
        print '%s\n' % result[0]
        print 'Round Winnings: %s' % result[1]
        self.winnings += result[1]
        print 'Total Winnings: %s' % self.winnings
        print '--------------------'


class Dealer():
    '''
    The dealer's implementation. Since the dealer's actions are taken care of in the __endHand__ 
    method from Game, this simply outputs the dealer's final hand and total.
    '''
    def __init__(self, game):
        self.game = game

    def playHand(self):
        '''
        Outputs dealer's final hand and total for the round.
        '''
        print 'Final Hand: %s' % self.hand
        print 'Final Total: %s\n' % self.total
 
class Oracle():
    '''
    The oracle implementation. This player evaluates all possible actions given the hand 
    and peeks into the deck to make the best possible move for each state, i.e. the perfect blackjack player.
    '''
    def __init__(self, game):
        self.game = game
        self.hand = []
        self.total = 0
    
    def playHand(self):
        '''
        Evaluates possible actions and takes actions with the highest reward for the current hand state until the hand is over.
        '''
        action = self.evaluateMoves()
        while action == self.game.hit:
            self.hand, self.total = action()
            print 'Hand: %s' % self.hand
            print 'Total: %s' % self.total
            action = self.evaluateMoves()
        if action != None:
            newState = action()
            if newState != None: 
                self.hand, self.total = newState
            if action != self.game.surrender:
                print 'Final Hand: %s' % self.hand
                print 'Final Total: %s\n' % self.total
        
    def evaluateMoves(self):
        '''
        Returns the action with the highest reward given the current hand state.
        '''
        moves = self.game.getPossibleActions()
        moveWinnings = []
        if self.game.stand in moves:
            moveWinnings.append((self.game.stand, self.standValue()))
        if self.game.hit in moves:
            moveWinnings.append((self.game.hit, self.hitValue()))
        if self.game.double in moves:
            moveWinnings.append((self.game.double, self.doubleValue()))
        if self.game.surrender in moves:
            moveWinnings.append((self.game.surrender, self.surrenderValue()))
        if len(moveWinnings) == 0: return None
        else: return max(moveWinnings, key = lambda pair:pair[1])[0]

    def standValue(self):
        '''
        Future value of standing on the given hand. Calls peekDealer() to see 
        how the hand will compare to the dealer's.
        '''
        return self.peekDealer(False)

    def hitValue(self):
        '''
        Future value of hitting on the given hand. Returns the negative bet if the player will bust, 
        otherwise returns 0.
        '''
        newCard = self.game.deck.peek()
        if self.total + self.game.cardValues[newCard] > 21:
            return -1 * self.game.bet
        else:
            return 0
    
    def doubleValue(self):
        '''
        Future value of doubling down on the given hand. Calls peekDealer() to see how the hand will 
        compare to the dealer's and returns the double the reward.
        '''
        return 2 * self.peekDealer(True)

    def surrenderValue(self):
        '''
        Future value of surrendering on the given hand, which is always losing half the bet.
        '''
        return self.game.bet / -2.0
        
    def peekDealer(self, doubling):
        '''
        Allows oracle to see into the future and peek at the hand that the dealer will have after 
        taking a given action (either stand or double). Uses doubling flag to indicate where in the deck 
        to start peeking. Returns future reward based on the comparison of player and dealer hands.
        '''
        playerTotal = self.total
        newIndex = -1
        if doubling:
            playerTotal += self.game.cardValues[self.game.getNextCard()]
            newIndex = -2
        dealerTotal = self.getDealerTotal(newIndex)
        return self.peekReward(playerTotal, dealerTotal)

    def getDealerTotal(self, newIndex):
        '''
        Plays out the dealer's hand and returns what the dealer's final total would be.
        Based on __endHand__ from Game.
        '''
        dealerTotal = self.game.dealerTotal
        dealerHand = self.game.dealerHand[:]
        while dealerTotal < 17:
            newCard = self.game.getDeck()[newIndex]
            dealerTotal += self.game.cardValues[newCard]
            dealerHand.append(newCard)
            if dealerTotal > 21:
                for index, card in enumerate(dealerHand):
                    if card == 'A':
                        dealerTotal -= 10
                        dealerHand[index] = 'a'
                        break
            newIndex -= 1
        return dealerTotal
       
    def peekReward(self, playerTotal, dealerTotal):
        '''
        Returns what the player's reward would be based on the comparison of the two hands. 
        Based on getReward() from Game.
        '''
        if playerTotal > 21:
            return -1 * self.game.bet
        if dealerTotal > 21:
            return self.game.bet
        if playerTotal > dealerTotal:
            return self.game.bet
        if playerTotal == dealerTotal:
            return 0
        else:
            return -1 * self.game.bet
