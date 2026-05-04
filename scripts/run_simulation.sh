#!/bin/bash
# run_simulation.sh - Launch full project pipeline
# FIX B19: BASE resolved dynamically from script location

BASE="$(cd "$(dirname "$0")/.." && pwd)"

echo "==============================="
echo " AI-based EE HetNet - Launcher"
echo " Project root: $BASE"
echo "==============================="

echo ""
echo "[1/5] NS2 Baseline simulation..."
ns "$BASE/ns2/scenario_baseline.tcl"

echo ""
echo "[2/5] NS2 Q-Learning simulation..."
ns "$BASE/ns2/scenario_ai.tcl"

echo ""
# FIX B20: DQN scenario was never launched
echo "[3/5] NS2 DQN simulation..."
ns "$BASE/ns2/scenario_dqn.tcl"

echo ""
echo "[4/5] Parse all traces..."
echo "-- Baseline --"
awk -f "$BASE/scripts/parse_ee.awk" "$BASE/results/baseline_trace.tr"
echo "-- Q-Learning --"
awk -f "$BASE/scripts/parse_ee.awk" "$BASE/results/ai_trace.tr"
echo "-- DQN --"
awk -f "$BASE/scripts/parse_ee.awk" "$BASE/results/dqn_trace.tr"

echo ""
echo "[5/5] Train Q-Learning + DQN, then generate figures..."
python3 "$BASE/python/train.py"
python3 "$BASE/python/plot_results.py"

echo ""
echo "Done! Results: $BASE/results/"
echo "      Figures: $BASE/figures/"
