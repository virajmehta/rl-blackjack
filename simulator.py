import random


# canonical encoding of cards to constants
# Ace:      A
# King:     K
# Queen:    Q
# Jack:     J
# numbers:  2-10

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
        

    def startHand(self, bet):
        '''Deals out the cards for a hand and returns ([dealerCard1, dealerCard2], [playerCard1, playerCard2], dealerTotal, playerTotal)'''

    def getReward(self):
        '''Call this whenever you're curious about the reward of a game state. If the hand is over, returns a value of the reward of that hand. If the hand isn't over, returns None'''

    def getPossibleActions(self):
        '''Returns all the possible actions of the current state in the form of a list of function pointers'''

    def getDeck(self):
        '''Returns a list containing all of the card values in the deck'''
        return self.deck.peekDeck()

    def __endHand__(self):


    def hit(self):
        '''Deals another card and returns (newCard, total) If total >= 21, game is over and reward will be not none'''

    def stand(self):
        '''Ends hand as is and does the dealer play. Call getReward to see what happens after. This function returns None'''

    def double(self):
        '''same as hit but doubles bet and lets the dealer play. Returns ([playerCard1, playerCard2, ...] , total). Call getReward to see what happened'''

    def surrender(self):
        '''ends game at beginning and returns None. Call getReward to see what happens after.'''

