'''This is the file containing all the code needed to have a simulated version of blackjack
canonical encoding of cards to constants
Ace:      A, a
King:     K
Queen:    Q
Jack:     J
numbers:  2-10'''
import random



class deck():
    '''This is the class that handles simulation for a deck of cards'''

    def __init__(self, numDecks, reshufflePercent):
        self.cards = []
        self.numDecks = numDecks
        self.reshufflePercent = reshufflePercent
        self.shuffle()

    def shuffle(self):
        '''Shuffles the deck and sets a new cut card'''
        self.cut = int(4 * self.numDecks * self.reshufflePercent * random.gauss(1, 0.2))
        self.cards = []
        for i in range(13):
            for j in range(4 * numDecks):
                card = i
                if i == 1:
                  card = 'A'
                elif i == 11:
                  card = 'J'
                elif i == 12:
                  card = 'Q'
                elif i == 13:
                  card = 'K'
                self.cards.append(i)
        random.shuffle(self.cards)


    def drawCard(self):
        '''draws a card'''
        self.cards.pop()
        return card

    def endHand(self):
        '''Hand is over. Check if need to shuffle. Return true if shuffled. False not'''
        if len(self.cards) < self.cut:
            return False
        else:
            self.shuffle()
            return True

    def peek(self):
        '''get the value of the next card in the deck. Useful for implementing a blackjack oracle'''
        if len(self.cards) == 0:
            return -1 # on error
        else:
            return self.cards[-1]

    def peekDeck(self):
        '''returns a copy of the list in the deck'''
        return self.cards[:]









class game():
    '''a game of blackjack. You call startHand to start and then getReward in between every action to see what the reward for the state would have been and whether the game is over. You can use getPossibleActions to figure out what actions are possible for you at any given state so you don't need the blackjack logic on the client end at all. If an impossible action is chosen, a function will return None and not do anything'''
    def __init__(self, numDecks=1):
        self.numDecks = numDecks
        self.deck = deck(self.numDecks, 0.25)
        self.playerHand = []
        self.dealerHand = []
        self.playerTotal = 0
        self.dealerTotal = 0
        self.bet = 0
        self.cardValues = {i : i for i in range(2, 11)}
        self.cardValues['K'] = 10
        self.cardValues['Q'] = 10
        self.cardValues['J'] = 10
        self.cardValues['A'] = 11
        self.cardValues['a'] = 1
        self.isBlackjack = False
        self.isOver = False

    def startHand(self, bet):
        '''Deals out the cards for a hand and returns ([dealerCard2], [playerCard1, playerCard2], dealerTotal, playerTotal)'''
        self.bet = bet
        for _ in range(2):
            self.playerHand.append(deck.drawCard())
            self.dealerHand.append(deck.drawCard())
        self.playerTotal = sum(self.cardValues[card] for card in playerHand)
        self.dealerTotal = sum(self.cardValues[card] for card in dealerHand)
        if self.playerTotal == 21 and self.dealerTotal != 21:
            self.isBlackjack = True
            self.isOver = True
        return (self.dealerHand[:], self.playerHand[:], self.dealerTotal, self.playerTotal)
        

    def getReward(self):
        '''Call this whenever you're curious about the reward of a game state. If the hand is over, returns a value of the reward of that hand and the cards in the final dealer hand as (reward, [dealerCard1, dealerCard2, ...]). If the hand isn't over, returns None'''
        if not self.isOver:
            return None
        if self.isBlackjack:
            return (1.5 * self.bet, self.dealerHand[:])
        if self.playerTotal > 21:
            return (-1 * bet, self.dealerHand[:])
        if self.dealerTotal > 21:
            return (bet, self.dealerHand[:])
        if self.playerTotal > self.dealerTotal:
            return (bet, self.dealerHand[:])
        else:
            return (-1 * bet, self.dealerHand[:])

    def getPossibleActions(self):
        '''Returns all the possible actions of the current state in the form of a list of function pointers'''
        moves = [self.hit, self.stand]
        if self.isOver:
            return []
        if len(self.playerHand) == 2:
            moves.append(self.double)
            moves.append(self.surrender)
        return moves

    def getAllActions(self):
        return [self.hit, self.stand, self.double, self.surrender]


    def getDeck(self):
        '''Returns a list containing all of the card values in the deck'''
        return self.deck.peekDeck()

    def __endHand__(self, dealerDraw=True):
        if dealerDraw:
            while self.dealerTotal < 17:
                newCard = self.deck.drawCard()
                self.dealerTotal += self.cardValues[newCard]
                self.dealerHand.append(newCard)
                if self.dealerTotal > 21:
                    for index, card in enumerate(self.dealerHand):
                        if card == 'A':
                            self.dealerTotal -= 10
                            self.dealerHand[index] = 'a' 
                            break
        self.deck.endHand()
        self.isOver = True

    def hit(self):
        '''Deals another card and returns (newCard, total) If total >= 21, game is over and reward will be not none'''
        newCard = self.deck.drawCard()
        self.playerTotal += self.cardValues[newCard]
        self.playerHand.append(newCard)
        if self.playerTotal == 21:
            self.__endHand__()
        elif self.playerTotal > 21:
            for index, card in enumerate(self.playerHand):
                if card == 'A':
                    self.playerTotal -= 10
                    self.playerHand[index] = 'a'
                    break
            if self.playerTotal > 21:
                self.__endHand__(False)
        return (newCard, self.playerTotal)

    def stand(self):
        '''Ends hand as is and does the dealer play. Call getReward to see what happens after. This function returns None'''
        self.__endHand__()

    def double(self):
        '''same as hit but doubles bet and lets the dealer play. Returns (newCard , total). Call getReward to see what happened'''
        newCard = self.deck.drawCard()
        self.playerTotal += self.cardValues[newCard]
        self.playerHand.append(newCard)
        if self.playerTotal > 21:
            for index, card in enumerate(self.playerHand):
                if card == 'A':
                    self.playerTotal -= 10
                    self.playerHand[index] = 'a'
                    break
        self.bet *= 2
        self.__endHand__()
        return (newCard, self.playerTotal)

    def surrender(self):
        '''ends game at beginning and returns None. Call getReward to see what happens after.'''
        self.bet /= 2
        self.playerTotal = 22
        self.__endHand__(False)
        return None

