'''
This is the file containing all the code needed for each type of blackjack player. 
It will eventually contain six player types: Dealer, Baseline, Oracle, Hi-Lo, Omega II, 
and Wong Halves. It currently contains the implementations for the first three.
'''
import time
from algorithms import QLearning
from simulator import Game

class Player(object):
    '''
    This is the class that wraps over the functions shared by each of the types of players.
    '''
    def __init__(self, name):
        self.game = Game()
        self.hand = []
        self.name = name
        self.player = None
        self.total = 0
        self.winnings = 0
    
    def playGame(self):
        '''
        Plays desired number of hands for given number of iterations.
        '''
        for _ in range(100):
            self.hand, self.total, _, _ = self.game.startHand(1)
            print '%s\'s Turn!\n' % self.name
            print 'Hand: %s' % self.hand
            print 'Total: %s' % self.total
            self.playHand()
            print 'Dealer\'s Turn!\n'
            print 'Final Hand: %s' % self.game.dealerHand
            print 'Final Total: %s\n' % self.game.dealerTotal
            self.getWinnings()

    def getWinnings(self):
        '''
        Calls getReward() from Game to retrieve the outcome of the hand. 
        Updates total winnings over the whole game.
        '''
        result, roundWinnings = self.game.getReward()
        print '%s\n' % result
        print 'Round Winnings: %s' % roundWinnings
        self.winnings += roundWinnings
        print 'Total Winnings: %s' % self.winnings
        print '--------------------'
        
class Baseline(Player):
    '''
    The baseline implementation. This player stands on every hand, regardless of the cards.
    '''
    def playHand(self):
        '''
        Calls stand() from Game to end the hand. Outputs final hand and total for the round.
        '''
        self.game.stand([])
        print 'Final Hand: %s' % self.hand
        print 'Final Total: %s\n' % self.total
 
class Oracle(Player):
    '''
    The oracle implementation. This player evaluates all possible actions given the hand 
    and peeks into the deck to make the best possible move for each state, 
    i.e. the perfect blackjack player.
    '''
    def playHand(self):
        '''
        Evaluates possible actions and takes actions with the highest reward for the 
        current hand state until the hand is over.
        '''
        action = self.evaluateMoves()
        while action == self.game.hit:
            self.hand, self.total = action([])
            print 'Hand: %s' % self.hand
            print 'Total: %s' % self.total
            action = self.evaluateMoves()
        if action != None:
            newState = action([])
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
        Future value of standing on the given hand. Calls peekDealer() to see how 
        the hand will compare to the dealer's.
        '''
        return self.peekDealer(False)

    def hitValue(self):
        '''
        Future value of hitting on the given hand. Returns the negative bet if the 
        player will bust, otherwise returns 0.
        '''
        newCard = self.game.deck.peek()
        if self.total + self.game.cardValues[newCard] > 21:
            return -1 * self.game.bet
        else:
            return 0
    
    def doubleValue(self):
        '''
        Future value of doubling down on the given hand. Calls peekDealer() to see how 
        the hand will compare to the dealer's and returns the double the reward.
        '''
        return 2 * self.peekDealer(True)

    def surrenderValue(self):
        '''
        Future value of surrendering on the given hand, which is always losing half the bet.
        '''
        return self.game.bet / -2.0
        
    def peekDealer(self, doubling):
        '''
        Allows oracle to see into the future and peek at the hand that the dealer will have 
        after taking a given action (either stand or double). Uses doubling flag to indicate 
        where in the deck to start peeking. Returns future reward based on the comparison 
        of player and dealer hands.
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


class RLPlayer(Player):
    def __init__(self, strat, algo):
        super(RLPlayer, self).__init__('RL')
        self.count = 0.0
        self.algo = QLearning(self.game, 'dqn') # we want the algo to take (state, pssible actions, reward) and return an action \in actions
        if strat == 'Hi-Lo':
            self.strat = self.hilo 
        elif strat == 'Omega II':
            self.strat = self.omega
        elif strat == 'Wong Halves':
            self.strat = self.wonghalf
        else:
            self.strat = None
        self.numAces = self.game.deck.getNumDecks() * 4# not always used
        '''here, self.strat is a utility function that returns the current count'''

    def train(self, numiter):
        ''' train an algorithm a number of iterations'''
        batch_size = 10000
        total_reward = 0.0
        winnings = 0.0
        for iter in xrange(numiter):
            if iter % batch_size == 0:
                print 'batch {}, avg reward {}'.format(iter / batch_size + 1, total_reward / batch_size)
                winnings += total_reward
                total_reward = 0.0

            shuffled = False #check for shuffle
            if self.game.deck.getNumCards() == self.game.deck.getNumDecks() * 52:
                shuffled = True

            countState = self.strat([], shuffled)
            state = (countState, 0, 0)

            #decide how to bet based on count
            #actions = ['big', 'small']
            #betlevel = self.algo.getAction(state, actions, 0)
            bet = 1 #if betlevel == 'small' else 10
            playerHand, playerTotal, dealerHand, turd = self.game.startHand(bet)
            dealerTotal = self.game.cardValues[dealerHand[0]]
            newCards =  playerHand + dealerHand
            countState = self.strat(newCards)
            state = (countState, playerTotal, dealerTotal)
            while state != None and not self.game.isOver:
                actions = self.game.getPossibleActions()
                newCards = []
                newState = None
                action = self.algo.getAction(state, actions)
                if action != None:
                    _, playerTotal = action(newCards)
                    countState = self.strat(newCards)
                    newState = (countState, playerTotal, dealerTotal)
                _, reward = self.game.getReward()
                total_reward += reward
                self.algo.incorporateFeedback(state, action, reward, newState)
                state = newState

        winnings = winnings / numiter
        print winnings
        time.sleep(2)

        
        winnings = 0.0
        total_reward = 0.0
        for iter in xrange(numiter):
            if iter % batch_size == 0:
                print 'batch {}, avg reward {}'.format(iter / batch_size + 1, total_reward / batch_size)
                winnings += total_reward
                total_reward = 0.0

            shuffled = False #check for shuffle
            if self.game.deck.getNumCards() == self.game.deck.getNumDecks() * 52:
                shuffled = True

            countState = self.strat([], shuffled)
            state = (countState, 0, 0)

            #decide how to bet based on count
            #actions = ['big', 'small']
            #betlevel = self.algo.getAction(state, actions, 0)
            bet = 1 #if betlevel == 'small' else 10
            playerHand, playerTotal, dealerHand, turd = self.game.startHand(bet)
            dealerTotal = self.game.cardValues[dealerHand[0]]
            newCards =  playerHand + dealerHand
            countState = self.strat(newCards)
            state = (countState, playerTotal, dealerTotal)
            while state != None:
                actions = self.game.getPossibleActions()
                newCards = []
                newState = None
                action = self.algo.getBestAction(state, actions)
                if action != None:
                    _, playerTotal = action(newCards)
                    countState = self.strat(newCards)
                    newState = (countState, playerTotal, dealerTotal)
                _, reward = self.game.getReward()
                total_reward += reward
                self.algo.incorporateFeedback(state, action, reward, newState)
                state = newState

        winnings = winnings / numiter
        print winnings



    def test(self, numiter):
        reward = 0.0
        for _ in xrange(numiter):
            shuffled = False
            if self.game.deck.getNumCards() == self.game.deck.getNumDecks() * 52:
                shuffled = True
            countState = self.strat([], shuffled=True)
            state = (countState, 0, 0)
            actions = ['big', 'small']
            betlevel = self.algo.getAction(state, actions, 0)
            bet = 1 #if betlevel == 'small' else 10
            playerHand, playerTotal, dealerHand, dealerTotal = self.game.startHand(bet)
            newCards =  playerHand + dealerHand
            countState = self.strat(newCards)
            state = (countState, playerHand, dealerHand)
            while len(actions) > 0:
                actions = self.game.getPossibleActions()
                reward = self.game.getReward()
                total_reward += reward
                action = self.algo.getAction(state, actions)
                newCards = []
                if action is not None:
                    playerHand, _ = action(newCards)
                    countState = self.strat(newCards)
        return reward / numiter
        
    def hilo(self, newCards, shuffled=False):
        if shuffled:
            self.count = 0.0
            return self.count
        countValues = {2:1, 3:1, 4:1, 5:1, 6:1, 7:0, 8:0, 9:0, 10:-1, 'J':-1, 'Q':-1, 'K':-1, 'A':-1, 'a':-1}
        for card in newCards:
            self.count += countValues[card]
        trueCount = self.count * self.game.deck.getNumCards() / 52.0
        return trueCount

    def omega(self, newCards, shuffled=False):
        if shuffled:
            self.count = 0.0
            self.numAces = self.game.deck.getNumDecks() * 4
            return (self.count, self.numAces)
        countValues = {2:1, 3:1, 4:2, 5:2, 6:2, 7:1, 8:0, 9:-1, 10:-2, 'J':-2, 'Q':-2, 'K':-2, 'A':0, 'a':0}
        for card in newCards:
            if card == 'a' or card == 'A':
                self.numAces -= 1
            self.count += countValues[card]
        trueCount = self.count * self.game.deck.getNumCards() / 52.0
        return (trueCount, self.numAces)


    def wonghalf(self, newCards, shuffled=False):
        if shuffled:
            self.count = 0.0
            self.numAces = self.game.deck.getNumDecks() * 4
            return self.count
        countValues = {2:0.5,3:1.0,4:1.0,5:1.5,6:1.0,7:0.5,8:0,9:-.5,10:-1,'J':-1,'Q':-1,'K':-1,'A':-1,'a':-1}
        for card in newCards:
            self.count += countValues[card]
        trueCount = self.count * self.game.deck.getNumCards() / 52.0
        return (trueCount, self.numAces)



