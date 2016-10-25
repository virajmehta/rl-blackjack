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








class game():
    def __init__(self, numDecks=1):
        self.numDecks = numDecks
    def 

