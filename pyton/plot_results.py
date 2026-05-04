# ============================================
# plot_results.py - Figures for ALL scenarios
# Baseline vs Q-Learning vs DQN
# ============================================

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os

# FIX B15/B16: dynamic paths relative to this script
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

WINDOW = 50  # moving average window


def load_csv(filename, fallback_len=500, fallback_val=None):
    """Load CSV with graceful fallback if file missing"""
    path = os.path.join(RESULTS_DIR, filename)
    if os.path.exists(path):
        return np.loadtxt(path, delimiter=",")
    print(f"  WARNING: {filename} not found — using fallback")
    return np.full(fallback_len, fallback_val if fallback_val is not None else 150.0)


def moving_avg(data, w):
    return np.convolve(data, np.ones(w) / w, mode='valid')


# ============================================================
# FIX B17/B18: Load ALL three scenarios
# ============================================================
energy_baseline = load_csv("energy_baseline.csv", fallback_val=150.0)
energy_q        = load_csv("energy_q.csv",        fallback_val=145.0)
energy_dqn      = load_csv("energy_dqn.csv",      fallback_val=143.0)
rewards_q       = load_csv("rewards_q.csv",        fallback_val=0.0)
rewards_dqn     = load_csv("rewards_dqn.csv",      fallback_val=0.0)

n = min(len(energy_baseline), len(energy_q), len(energy_dqn))
energy_baseline = energy_baseline[:n]
energy_q        = energy_q[:n]
energy_dqn      = energy_dqn[:n]
rewards_q       = rewards_q[:n]
rewards_dqn     = rewards_dqn[:n]
episodes        = np.arange(1, n + 1)

# ============================================================
# FIGURE 1 — Energy comparison: Baseline vs Q-Learning vs DQN
# ============================================================
fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(episodes, energy_baseline, 'r--', linewidth=2,   alpha=0.7, label='Baseline (no AI)')
ax.plot(episodes, energy_q,        'b-',  linewidth=1,   alpha=0.35, label='Q-Learning (raw)')
ax.plot(episodes, energy_dqn,      'g-',  linewidth=1,   alpha=0.35, label='DQN (raw)')

# Moving averages
ma_q   = moving_avg(energy_q,   WINDOW)
ma_dqn = moving_avg(energy_dqn, WINDOW)
ax.plot(episodes[WINDOW-1:], ma_q,   'b-', linewidth=2.5, label=f'Q-Learning (MA {WINDOW}ep)')
ax.plot(episodes[WINDOW-1:], ma_dqn, 'g-', linewidth=2.5, label=f'DQN (MA {WINDOW}ep)')

ax.set_xlabel('Episode', fontsize=12)
ax.set_ylabel('Average Energy (W)', fontsize=12)
ax.set_title('Energy Comparison: Baseline vs Q-Learning vs DQN', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Annotations — final savings
last = slice(max(0, n - WINDOW), n)
saving_q   = np.mean(energy_baseline[last]) - np.mean(energy_q[last])
saving_dqn = np.mean(energy_baseline[last]) - np.mean(energy_dqn[last])
ax.annotate(f'Q-Learning saves {saving_q:.1f}W ({saving_q/150*100:.1f}%)',
            xy=(n, np.mean(energy_q[last])),   xytext=(n * 0.7, np.mean(energy_q[last])   - 3),
            fontsize=9, color='blue', arrowprops=dict(arrowstyle='->', color='blue', lw=0.8))
ax.annotate(f'DQN saves {saving_dqn:.1f}W ({saving_dqn/150*100:.1f}%)',
            xy=(n, np.mean(energy_dqn[last])), xytext=(n * 0.7, np.mean(energy_dqn[last]) - 3),
            fontsize=9, color='green', arrowprops=dict(arrowstyle='->', color='green', lw=0.8))

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "energy_comparison.png"), dpi=150)
plt.close()
print("Saved: energy_comparison.png")

# ============================================================
# FIGURE 2 — Convergence: Q-Learning and DQN rewards
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Q-Learning convergence
axes[0].plot(episodes, rewards_q,  color='orange', alpha=0.35, linewidth=1,   label='Reward (raw)')
ma_rq = moving_avg(rewards_q, WINDOW)
axes[0].plot(episodes[WINDOW-1:], ma_rq, color='darkred',  linewidth=2.5, label=f'MA {WINDOW}ep')
axes[0].axhline(0, color='gray', linestyle='--', linewidth=1)
axes[0].set_title('Q-Learning Convergence', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Episode')
axes[0].set_ylabel('Total Reward per Episode')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# DQN convergence
axes[1].plot(episodes, rewards_dqn,  color='cyan',  alpha=0.35, linewidth=1,   label='Reward (raw)')
ma_rdqn = moving_avg(rewards_dqn, WINDOW)
axes[1].plot(episodes[WINDOW-1:], ma_rdqn, color='darkgreen', linewidth=2.5, label=f'MA {WINDOW}ep')
axes[1].axhline(0, color='gray', linestyle='--', linewidth=1)
axes[1].set_title('DQN Convergence', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Episode')
axes[1].set_ylabel('Total Reward per Episode')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.suptitle('Training Convergence: Q-Learning vs DQN', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "convergence_comparison.png"), dpi=150, bbox_inches='tight')
plt.close()
print("Saved: convergence_comparison.png")

# ============================================================
# FIGURE 3 — Summary bar chart (final 50 episodes)
# ============================================================
labels  = ['Baseline', 'Q-Learning', 'DQN']
values  = [
    np.mean(energy_baseline[last]),
    np.mean(energy_q[last]),
    np.mean(energy_dqn[last]),
]
colors  = ['#e74c3c', '#3498db', '#2ecc71']
savings = [0, values[0] - values[1], values[0] - values[2]]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=1.2, width=0.5)

for bar, val, sav in zip(bars, values, savings):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{val:.1f}W', ha='center', va='bottom', fontsize=11, fontweight='bold')
    if sav > 0:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                f'-{sav:.1f}W\n({sav/values[0]*100:.1f}%)',
                ha='center', va='center', fontsize=10, color='white', fontweight='bold')

ax.set_ylabel('Average Energy (W)', fontsize=12)
ax.set_title('Final Energy Summary (last 50 episodes)', fontsize=13, fontweight='bold')
ax.set_ylim(0, max(values) * 1.15)
ax.grid(axis='y', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "energy_summary_bar.png"), dpi=150)
plt.close()
print("Saved: energy_summary_bar.png")

# ============================================================
# Print summary to console
# ============================================================
print("\n=== SUMMARY ===")
print(f"  Baseline   avg energy : {values[0]:.2f} W")
print(f"  Q-Learning avg energy : {values[1]:.2f} W  (saves {savings[1]:.2f}W / {savings[1]/values[0]*100:.1f}%)")
print(f"  DQN        avg energy : {values[2]:.2f} W  (saves {savings[2]:.2f}W / {savings[2]/values[0]*100:.1f}%)")
print(f"\nFigures saved in: {FIGURES_DIR}")
