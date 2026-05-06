
# ⚡ AI-based Energy Efficiency in HetNet

## 📖 Description
Simulation d'un réseau hétérogène (**HetNet**) avec optimisation de la consommation énergétique par :
- Q-Learning  
- Deep Q-Learning (DQN)

---

## 📁 Structure du projet
# 0. created the diroctore
#  cd ~
#  mkdire Projet_EE_HetNet
# cd Projet_EE_HetNet

```bash
Projet_EE_HetNet/
├── ns2/
│   ├── scenario_baseline.tcl   # HetNet SANS IA (référence)
│   ├── scenario_ai.tcl         # HetNet avec Q-Learning
│   └── scenario_dqn.tcl        # HetNet avec DQN
├── python/
│   ├── environment.py          # Modèle HetNet (états/actions/rewards)
│   ├── qlearning_agent.py      # Agent Q-Learning
│   ├── dqn_agent.py            # Agent Deep Q-Learning (DQN)
│   ├── train.py                # Entraînement Q-Learning + DQN
│   ├── communication.py        # Interface NS2 <-> Python
│   └── plot_results.py         # Génération graphiques
├── results/
│   ├── q_table.json
│   ├── energy_ai.csv
│   ├── rewards.csv
│   ├── baseline_trace.tr
│   ├── ai_trace.tr
│   ├── dqn_trace.tr
│   └── resultats_comparison.txt
├── figures/
│   ├── energy_comparison.png
│   └── qlearning_convergence.png
└── scripts/
    ├── run_simulation.sh
    └── parse_ee.awk

Résultats
Métrique	Baseline	Q-Learning
Énergie moyenne	150.0 W	144.94 W
Économie	-	5.06 W (3.4%)

Lancer le projet

# 1. Tout lancer automatiquement
bash scripts/run_simulation.sh

# Ou étape par étape :
# 2. Simulation NS2 baseline
ns ns2/scenario_baseline.tcl

# 3. Simulation NS2 avec Q-Learning
ns ns2/scenario_ai.tcl

# 4. Simulation NS2 avec DQN
ns ns2/scenario_dqn.tcl

# 5. Entraînement Q-Learning + DQN
python3 python/train.py

# 6. Générer les graphiques
python3 python/plot_results.py

############# attation you need tanserflow in your env for DQN
