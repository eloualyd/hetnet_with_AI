# ============================================
# dqn_agent.py - Agent Deep Q-Learning (DQN)
# ============================================

import numpy as np
import random
from collections import deque
import tensorflow as tf
from tensorflow.keras import layers
# FIX B1: removed unused 'import json'


class DQNAgent:
    def __init__(self, num_states, num_actions,
                 gamma=0.9, epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.995,
                 learning_rate=0.001, target_update_freq=10):

        self.num_states = num_states
        self.num_actions = num_actions
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate

        # FIX B4: target network update frequency counter
        self.target_update_freq = target_update_freq
        self.step_count = 0

        self.memory = deque(maxlen=2000)

        # FIX B4: main model + separate frozen target model
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_network()

    def _build_model(self):
        model = tf.keras.Sequential([
            layers.Dense(24, activation='relu', input_shape=(self.num_states,)),
            layers.Dense(24, activation='relu'),
            layers.Dense(self.num_actions, activation='linear')
        ])
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse'
        )
        return model

    def update_target_network(self):
        """Copy weights from main model to frozen target model (FIX B4)"""
        self.target_model.set_weights(self.model.get_weights())

    def choose_action(self, state):
        """Epsilon-greedy"""
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.num_actions)
        state = np.reshape(state, [1, self.num_states])
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])

    def remember(self, state, action, reward, next_state, done):
        # FIX B2: added done flag for correct Bellman at terminal states
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)

        # FIX B3: build full batch arrays — single predict + single fit
        states      = np.reshape([s  for s,a,r,ns,d in minibatch], [batch_size, self.num_states]).astype(np.float32)
        next_states = np.reshape([ns for s,a,r,ns,d in minibatch], [batch_size, self.num_states]).astype(np.float32)

        # FIX B4: use frozen target_model for stable Q-targets
        current_q = self.model.predict(states,      verbose=0)
        target_q  = self.target_model.predict(next_states, verbose=0)

        for idx, (state, action, reward, next_state, done) in enumerate(minibatch):
            # FIX B2: terminal state → no future reward
            new_q = reward if done else reward + self.gamma * np.max(target_q[idx])
            current_q[idx][action] = new_q

        # FIX B3: single fit on the full batch (was 32 separate fits)
        self.model.fit(states, current_q, epochs=1, verbose=0, batch_size=batch_size)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # FIX B4: periodically sync target network
        self.step_count += 1
        if self.step_count % self.target_update_freq == 0:
            self.update_target_network()

    def save(self, path="dqn_model.keras"):
        # FIX B5: .keras format (.h5 is deprecated in TF 2.x)
        self.model.save(path)
        print(f"Model saved: {path}")

    def load(self, path="dqn_model.keras"):
        # FIX B5: .keras format
        self.model = tf.keras.models.load_model(path)
        self.update_target_network()
        print(f"Model loaded: {path}")
