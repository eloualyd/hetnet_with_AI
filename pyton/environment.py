# ============================================
# environment.py - HetNet Environment (Q-learning + DQN)
# ============================================

import numpy as np


class HetNetEnvironment:
    def __init__(self, num_small_cells=2):

        self.num_small_cells = num_small_cells
        self.num_states  = 3
        self.num_actions = 4

        # Energy model (Watts)
        self.energy_macro    = 150
        self.energy_small_on = 30
        self.energy_small_off = 5

        self.last_energy = self.energy_macro

    # ============================================
    # Q-LEARNING STATE (discrete)
    # ============================================
    def get_state(self, users):
        """
        Discrete state for Q-learning:
        0 = low load  (<10 users)
        1 = medium    (10-17 users)
        2 = high      (>=18 users)
        """
        if users < 10:
            return 0
        elif users < 18:
            return 1
        else:
            return 2

    # ============================================
    # DQN STATE (continuous vector)
    # ============================================
    def get_state_vector(self, users):
        """
        Continuous normalized state for DQN — 3 distinct features.
        FIX B6: users_norm and load were identical (both = users/25.0).
                 Now each feature is meaningfully different.
        """
        users_norm  = users / 25.0                      # raw user density [0,1]
        load_level  = self.get_state(users) / 2.0       # discrete load (0, 0.5, 1.0)
        cells_ratio = self.num_small_cells / 2.0        # small cells fraction [0,1]

        return np.array([users_norm, load_level, cells_ratio], dtype=np.float32)

    # ============================================
    # STEP
    # ============================================
    def step(self, action, users):
        """
        Apply action → return (next_state, reward, energy, done).
        FIX B7: removed unused 'state = get_state(users)' variable.
        """
        # Energy model
        if action == 0:
            energy = self.energy_macro
        elif action == 1:
            energy = self.energy_macro * 0.95
        elif action == 2:
            energy = self.energy_macro * 0.90
        else:
            energy = self.energy_macro * 0.85

        self.last_energy = energy

        # Reward function
        reward = (self.energy_macro - energy)    # energy saving

        if users > 20 and action == 0:           # overload penalty
            reward -= 20

        if users < 15:                           # stability bonus
            reward += 5

        next_state = self.get_state(users)
        done = False  # continuous environment — no terminal state

        return next_state, reward, energy, done
