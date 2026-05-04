# ============================================
# train.py - Q-Learning vs DQN comparison HetNet
# ============================================

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from environment import HetNetEnvironment
from qlearning_agent import QLearningAgent
from dqn_agent import DQNAgent

# ---- Parameters ----
NUM_EPISODES  = 500
MAX_STEPS     = 50
NUM_USERS_MAX = 25

# FIX B8: dynamic path relative to this script, not hardcoded /home/
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def simulate_users(step):
    t = step / MAX_STEPS
    base = 10 + 15 * np.sin(np.pi * t)
    noise = np.random.randint(-3, 4)
    return int(np.clip(base + noise, 0, NUM_USERS_MAX))


# ============================================
# TRAIN Q-LEARNING
# ============================================
def train_qlearning():
    print("\n=== TRAIN Q-LEARNING ===")

    env   = HetNetEnvironment(num_small_cells=2)
    agent = QLearningAgent(num_states=3, num_actions=4)

    rewards, energy = [], []

    for ep in range(NUM_EPISODES):
        state = env.get_state(simulate_users(0))
        total_r, total_e = 0, 0

        for step in range(MAX_STEPS):
            action = agent.choose_action(state)
            users  = simulate_users(step)

            # FIX B8: step() now returns 4 values (added done)
            next_state, reward, e, done = env.step(action, users)
            agent.update(state, action, reward, next_state)

            state    = next_state
            total_r += reward
            total_e += e

        rewards.append(total_r)
        energy.append(total_e / MAX_STEPS)

        if (ep + 1) % 100 == 0:
            print(f"  Episode {ep+1}/{NUM_EPISODES} | avg energy: {np.mean(energy[-100:]):.2f}W")

    agent.save(os.path.join(RESULTS_DIR, "q_table.json"))
    return rewards, energy


# ============================================
# TRAIN DQN
# ============================================
def train_dqn():
    print("\n=== TRAIN DQN ===")

    env = HetNetEnvironment(num_small_cells=2)

    # FIX B10: use env attributes directly (consistent)
    state_size  = env.num_states
    action_size = env.num_actions

    agent = DQNAgent(state_size, action_size)

    rewards, energy = [], []

    for ep in range(NUM_EPISODES):
        # DQN uses continuous state vector
        state = env.get_state_vector(simulate_users(0))
        total_r, total_e = 0, 0

        for step in range(MAX_STEPS):
            action = agent.choose_action(state)
            users  = simulate_users(step)

            # FIX B10: get env step result, then build DQN vector consistently
            _, reward, e, done = env.step(action, users)
            next_state = env.get_state_vector(users)

            # FIX B9: pass done flag to remember()
            agent.remember(state, action, reward, next_state, done)
            agent.replay(batch_size=32)

            state    = next_state
            total_r += reward
            total_e += e

        rewards.append(total_r)
        energy.append(total_e / MAX_STEPS)

        if (ep + 1) % 100 == 0:
            print(f"  Episode {ep+1}/{NUM_EPISODES} | avg energy: {np.mean(energy[-100:]):.2f}W | epsilon: {agent.epsilon:.3f}")

    # FIX B5: save as .keras (not .h5)
    agent.save(os.path.join(RESULTS_DIR, "dqn_model.keras"))
    return rewards, energy


# ============================================
# BASELINE (no AI — constant energy)
# ============================================
def compute_baseline():
    """Simulated baseline: always action 0 (full power = 150W)"""
    print("\n=== BASELINE (no AI) ===")
    env = HetNetEnvironment(num_small_cells=2)
    energy = []
    for ep in range(NUM_EPISODES):
        total_e = 0
        for step in range(MAX_STEPS):
            users = simulate_users(step)
            _, _, e, _ = env.step(0, users)   # action 0 = always full power
            total_e += e
        energy.append(total_e / MAX_STEPS)
    print(f"  Baseline avg energy: {np.mean(energy):.2f}W")
    return energy


# ============================================
# MAIN
# ============================================
def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    baseline_energy        = compute_baseline()
    q_rewards, q_energy    = train_qlearning()
    dqn_rewards, dqn_energy = train_dqn()

    # Save all CSVs for plot_results.py
    np.savetxt(os.path.join(RESULTS_DIR, "energy_baseline.csv"), baseline_energy,  delimiter=",")
    np.savetxt(os.path.join(RESULTS_DIR, "energy_q.csv"),        q_energy,         delimiter=",")
    np.savetxt(os.path.join(RESULTS_DIR, "rewards_q.csv"),       q_rewards,        delimiter=",")
    np.savetxt(os.path.join(RESULTS_DIR, "energy_dqn.csv"),      dqn_energy,       delimiter=",")
    np.savetxt(os.path.join(RESULTS_DIR, "rewards_dqn.csv"),     dqn_rewards,      delimiter=",")

    print("\n=== FINAL COMPARISON (last 50 episodes) ===")
    print(f"  Baseline avg energy  : {np.mean(baseline_energy[-50:]):.2f} W")
    print(f"  Q-Learning avg energy: {np.mean(q_energy[-50:]):.2f} W")
    print(f"  DQN avg energy       : {np.mean(dqn_energy[-50:]):.2f} W")


if __name__ == "__main__":
    main()
