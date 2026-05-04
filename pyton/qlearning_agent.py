# ============================================
# qlearning_agent.py - Agent Q-Learning
# ============================================

import numpy as np
import json

class QLearningAgent:
    def __init__(self, num_states, num_actions,
                 alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.99991):
        self.num_states   = num_states
        self.num_actions  = num_actions
        self.alpha        = alpha        # taux d'apprentissage
        self.gamma        = gamma        # facteur d'actualisation
        self.epsilon      = epsilon      # exploration initiale
        self.epsilon_min  = epsilon_min
        self.epsilon_decay= epsilon_decay

        # Table Q initialisee a zero
        self.q_table = np.zeros((num_states, num_actions))

    def choose_action(self, state):
        """Epsilon-greedy : exploration vs exploitation"""
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.num_actions)  # exploration
        return np.argmax(self.q_table[state])            # exploitation

    def update(self, state, action, reward, next_state):
        """Mise a jour Q-table"""
        best_next = np.max(self.q_table[next_state])
        td_target = reward + self.gamma * best_next
        td_error  = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.alpha * td_error

        # Reduire epsilon progressivement
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, path="q_table.json"):
        data = {"q_table": self.q_table.tolist(), "epsilon": self.epsilon}
        with open(path, "w") as f:
            json.dump(data, f)
        print(f"Q-table sauvegardee : {path}")

    def load(self, path="q_table.json"):
        with open(path, "r") as f:
            data = json.load(f)
        self.q_table = np.array(data["q_table"])
        self.epsilon = data["epsilon"]
        print(f"Q-table chargee : {path}")

    def print_q_table(self):
        print("\n=== Q-TABLE ===")
        print(f"{'State':<8} {'A00':>8} {'A01':>8} {'A10':>8} {'A11':>8}")
        labels = ["low", "medium", "high"]
        for s in range(self.num_states):
            row = " ".join(f"{self.q_table[s][a]:>8.2f}" for a in range(self.num_actions))
            print(f"{labels[s]:<8} {row}")


# ---- Test rapide ----
if __name__ == "__main__":
    agent = QLearningAgent(num_states=3, num_actions=4)
    print("Agent cree.")
    # Simuler quelques updates manuelles
    agent.update(state=1, action=1, reward=9.0,  next_state=1)
    agent.update(state=1, action=0, reward=-12.0, next_state=1)
    agent.update(state=2, action=3, reward=0.0,  next_state=2)
    agent.print_q_table()
