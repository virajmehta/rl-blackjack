from collections import defaultdict
import math, random

class QLearning():
    def __init__(self, game, discount=1, explorationProb=0.2):
        self.game = game
        self.discount = discount
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.numIters = 0

    def getQ(self, state, action):
        featureKey = tuple((state, action))
        featureValue = 1
        return self.weights[featureKey] * featureValue

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

    def incorporateFeedback(self, state, action, reward, newState):
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
