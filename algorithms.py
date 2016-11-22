from collections import defaultdict
import math, random
import numpy as np

class QLearning():
    def __init__(self, game, qLearnType='basic', discount=1, explorationProb=0.2):
        self.game = game
        self.discount = discount
        self.explorationProb = explorationProb
        self.numIters = 0
        if qLearnType == 'basic':
            self.getQ = self.naive
            self.incorporateFeedback = self.evian
            self.weights = defaultdict(float)
        elif qLearnType == 'linear':
            self.getQ = self.linear
            self.incorporateFeedback = self.linearSGD
            self.weights = { game.hit:    np.zeros(42),
                             game.stand:  np.zeros(42),
                             game.double: np.zeros(42),
                             game.surrender: np.zeros(42),
                             'small':     np.zeros(42),
                             'big':       np.zeros(42) }
        #deep goes here

    def naive(self, state, action):
        featureKey = tuple((state, action))
        featureValue = 1
        return self.weights[featureKey] * featureValue

    def phi(self, state): # state = (count, playerTotal, dealerTotal)
        phi = np.zeros(42)
        phi[0] = state[0] # count
        phi[1] = state[1] # player total
        phi[state[1]] = 1 # player indicator
        phi[31] = state[2]#dealer total
        phi[30 + state[2]] = 1 # dealer indicator
        return phi
        

    def linear(self, state, action):
        if action is None:
            return 0
        theta = self.weights[action]
        return np.dot(theta, self.phi(state))

    def getAction(self, state, actions):
        self.numIters += 1
        if len(actions) == 0: return None
        if random.random() < self.explorationProb:
            return random.choice(actions)
        else:
            return max((self.getQ(state, action), action) for action in actions)[1]

    def getBestAction(self, state, actions):
        self.numIters += 1
        if len(actions) == 0: return None
        return max((self.getQ(state, action), action) for action in actions)[1]

    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    def evian(self, state, action, reward, newState):
        key = (state, action)
        eta = self.getStepSize()
        r = reward
        gamma = self.discount
        Q_opt = 0
        V_opt = 0
        if not self.game.isOver:
            Q_opt = self.getQ(state, action)
            V_opt = max(self.getQ(newState, a) \
                for a in self.game.getPossibleActions())
        self.weights[key] = self.weights[key] - eta * (Q_opt - (r + gamma * V_opt))

    def linearSGD(self, state, action, reward, newState):
        gamma = self.discount
        V_opt = 0
        if not self.game.isOver:
            V_opt = max(self.getQ(newState, a) \
                for a in self.game.getPossibleActions())
        yHat = gamma * V_opt + reward
        yPred = self.getQ(state, action)
        phi = self.phi(state)
        error = yHat - yPred
        update = phi * error * self.getStepSize()
        if action is not None:
            self.weights[action] = np.add(self.weights[action], update)
