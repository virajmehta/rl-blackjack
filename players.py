from simulator import Game 

class Player():
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
        for _ in range(10):
            state = self.game.startHand(1)
            print '%s\'s Turn!\n' % self.playerName
            self.player.hand = state[1]
            print 'Hand: %s' % self.player.hand
            self.player.total = state[3]
            print 'Total: %s' % self.player.total
            self.player.playHand()
            self.dealer.playHand()
            self.getWinnings()

    def getWinnings(self):
        result = self.game.getReward()
        print '%s\n' % result[0]
        print 'Round Winnings: %s' % result[1]
        self.winnings += result[1]
        print 'Total Winnings: %s' % self.winnings
        print '--------------------'


class Dealer():
    def __init__(self, game):
        self.game = game

    def playHand(self):
        print 'Dealer\'s Turn!\n'
        print 'Final Hand: %s' % self.game.dealerHand
        print 'Final Total: %s\n' % self.game.dealerTotal

class Baseline():
    def __init__(self, game):
        self.game = game
    
    def playHand(self):
        self.game.stand()
        print 'Final Hand: %s' % self.game.playerHand
        print 'Final Total: %s\n' % self.game.playerTotal
 
class Oracle():
    def __init__(self, game):
        self.game = game
        self.hand = []
        self.total = 0
    
    def playHand(self):
        action = self.evaluateMoves()
        while action == self.game.hit and action != None:
            action()
            self.hand = self.game.playerHand
            self.total = self.game.playerTotal
            print 'Hand: %s' % self.hand
            print 'Total: %s' % self.total
            action = self.evaluateMoves()
        
        if action != None:
            action()
            if action != self.game.surrender:
                print 'Final Hand: %s' % self.game.playerHand
                print 'Final Total: %s\n' % self.game.playerTotal
        else:
            print '\n'
        
    def evaluateMoves(self):
        moves = self.game.getPossibleActions()
        if self.game.isBlackjack: return None
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
        return self.peekDealer(False)

    def hitValue(self):
        newCard = self.game.deck.peek()
        if self.total + self.game.cardValues[newCard] > 21:
            return -1 * self.game.bet
        else:
            return 0
    
    def doubleValue(self):
        return 2 * self.peekDealer(True)

    def surrenderValue(self):
        return self.game.bet / -2.0
        
    def peekDealer(self, doubling):
        playerTotal = self.game.playerTotal
        deck = self.game.deck.peekDeck()
        newIndex = -1
        if doubling:
            playerTotal += self.game.cardValues[deck[-1]]
            newIndex = -2
        dealerTotal = self.getDealerTotal(newIndex, deck)
        return self.peekReward(playerTotal, dealerTotal)

    def getDealerTotal(self, newIndex, deck):
        dealerTotal = self.game.dealerTotal
        dealerHand = [x for x in self.game.dealerHand]
        while dealerTotal < 17:
            newCard = deck[newIndex]
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
