from collections import defaultdict
import math, random, os
import numpy as np
import tensorflow as tf



class QLearning():


    def __init__(self, game, qLearnType='basic', discount=1, explorationProb=0.2):
        self.game = game
        self.kActionIndex = { #action index in Q vectors for deep learning
            game.hit:   0,
            game.stand: 1,
            game.double: 2,
            game.surrender: 3,
            'small': 4,
            'big': 5
        }
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
        elif qLearnType == 'dqn':
            self.qNet = Qnetwork()
            self.getQ = self.DQNEval
            self.incorporateFeedback = self.DQNTrain
            self.buffer = [[], [],[]] #states, actions, targetQ
            self.cacheState = None
            self.cacheQ = None
        #deep goes here

    def DQNEval(self, state, action):
        if self.cacheState != state:
            self.cacheQ = np.reshape(self.qNet.get_action_scores(self.phi(state)), (6,))
            self.cacheState = state
        return self.cacheQ[self.kActionIndex[action]]

    def DQNTrain(self, state, action, reward, newState):
        if action is None:
            import pdb; pdb.set_trace()
        self.buffer[0].append(self.phi(state))
        action1hot = np.zeros(6)
        action1hot[self.kActionIndex[action]] = 1
        self.buffer[1].append(action1hot)
        if newState is None:
            self.buffer[2].append(reward)
            return
        actions = self.game.getPossibleActions()
        if self.cacheState != newState:
            self.cacheState = newState
            self.cacheQ = np.reshape(self.qNet.get_action_scores(self.phi(state)), (6,))
        maxQ = -1000000.0 if len(actions) > 0 else 0.0
        for action in actions:
            if maxQ < self.cacheQ[self.kActionIndex[action]]:
                maxQ =  self.cacheQ[self.kActionIndex[action]]
        targetQ = maxQ*self.discount + reward
        self.buffer[2].append(targetQ)
        if len(self.buffer[0]) >= 50:
            self.qNet.trainBatch(self.buffer)
            buffer = [[], [], []]



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

kLearningRate = 0.01
class Qnetwork():
    def __init__(self):
        self.path = './dqn'
        if not os.path.exists(self.path):
            os.chmod(self.path, 0777)
            os.makedirs(self.path)
        self.weights = {
            # first layer of FC layers, 42 inputs, 40 outputs
            'wfc1': tf.Variable(tf.random_normal([42, 40])),
            # second layer of FC layers, 40 outputs, 30 outputs
            'wfc2': tf.Variable(tf.random_normal([40, 30])),
            # third layer FC, 30 inputs, 20 outputs
            'wfc3': tf.Variable(tf.random_normal([30, 20])),
            # fourth layer FC, 20 inputs, 6 outputs
            'wfc4': tf.Variable(tf.random_normal([20, 6]))
        }
        self.biases = {
            'bfc1': tf.Variable(tf.random_normal([40])),
            'bfc2': tf.Variable(tf.random_normal([30])),
            'bfc3': tf.Variable(tf.random_normal([20])),
            'bfc4': tf.Variable(tf.random_normal([6]))
        }
        self.phi = tf.placeholder(tf.float32, shape=[None, 42])
        fc1 = tf.add(tf.matmul(self.phi, self.weights['wfc1']), self.biases['bfc1'])
        fc1 = tf.nn.relu(fc1)
        # dropout?
        # fc1 = tf.nn.dropout(fc1, kDropout)
        fc2 = tf.add(tf.matmul(fc1, self.weights['wfc2']), self.biases['bfc2'])
        fc2 = tf.nn.relu(fc2)
        # fc2 = tf.nn.dropout(fc1, kDropout)
        fc3 = tf.add(tf.matmul(fc2, self.weights['wfc3']), self.biases['bfc3'])
        fc3 = tf.nn.relu(fc3)
        # fc3 = tf.nn.dropout(fc3, kDropout)
        fc4 = tf.add(tf.matmul(fc3, self.weights['wfc4']), self.biases['bfc4'])
        fc4 = tf.nn.relu(fc4)
        self.output = fc4
        self.targetQ = tf.placeholder(tf.float32, shape=[None, 1])
        self.actions = tf.placeholder(tf.float32, shape=[None, 6])
        qVals = tf.mul(self.actions, self.output)
        self.Q = tf.reduce_max(qVals, axis=0)
        self.error = tf.square(self.targetQ - self.Q)
        self.loss = tf.reduce_mean(self.error)
        self.trainer = tf.train.GradientDescentOptimizer(learning_rate=kLearningRate)
        self.updateModel = self.trainer.minimize(self.loss)
        self.init = tf.global_variables_initializer()
        self.sess = tf.Session()
        self.sess.run(self.init)
        self.batchNum =0
        self.saver = tf.train.Saver()


    def get_action_scores(self, phi):
        feed_dict = {self.phi: np.reshape(phi, (1, -1))}
        with self.sess.as_default():
            return self.output.eval(feed_dict=feed_dict)

    def trainBatch(self, batch):
        '''here, batch is a list of lists [[states],[actions],[targetQ]]'''
        self.batchNum += 1
        old_states = np.array(batch[0])
        actions = np.array(batch[1])
        target_Q = np.array(batch[2]).reshape((-1, 1))
        with self.sess.as_default():
            self.sess.run(self.updateModel, feed_dict={
                self.phi: old_states,
                self.actions: actions,
                self.targetQ: target_Q
            })
            if self.batchNum %10000 == 0:
                self.saver.save(self.sess, self.path+'/model-'+str(self.batchNum)+'.cptk')
                print 'Saved Model'




#not doing expereince replay, explain why


