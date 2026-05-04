# ============================================
# communication.py - Interface NS2 <-> Python
# ============================================

import subprocess
import os

# FIX B12: dynamic path relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NS2_PATH         = "ns"
BASELINE_SCRIPT  = os.path.join(BASE_DIR, "ns2", "scenario_baseline.tcl")
AI_SCRIPT        = os.path.join(BASE_DIR, "ns2", "scenario_ai.tcl")
# FIX B14: DQN script was missing
DQN_SCRIPT       = os.path.join(BASE_DIR, "ns2", "scenario_dqn.tcl")
RESULTS_DIR      = os.path.join(BASE_DIR, "results")


def run_ns2_simulation(script_path):
    """Run an NS2 simulation and return stdout"""
    print(f"Launching NS2: {os.path.basename(script_path)}")
    result = subprocess.run(
        [NS2_PATH, script_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"NS2 ERROR:\n{result.stderr}")
        return None
    print(result.stdout)
    return result.stdout


def parse_trace_file(trace_path):
    """
    Parse NS2 .tr file → extract sent/received/dropped/PDR
    """
    if not os.path.exists(trace_path):
        print(f"Trace file not found: {trace_path}")
        return None

    sent = received = dropped = 0

    with open(trace_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            event = parts[0]
            if event == '+': sent     += 1
            elif event == 'r': received += 1
            elif event == 'd': dropped  += 1

    pdr = (received / sent * 100) if sent > 0 else 0
    return {
        "sent":     sent,
        "received": received,
        "dropped":  dropped,
        "pdr":      round(pdr, 2)
    }


def compare_traces():
    """
    Compare baseline vs Q-Learning vs DQN traces.
    FIX B13 + B14: now includes DQN trace.
    """
    traces = {
        "Baseline":   os.path.join(RESULTS_DIR, "baseline_trace.tr"),
        "Q-Learning": os.path.join(RESULTS_DIR, "ai_trace.tr"),
        "DQN":        os.path.join(RESULTS_DIR, "dqn_trace.tr"),
    }

    print("\n=== NS2 TRACE COMPARISON ===")
    results = {}
    for label, path in traces.items():
        stats = parse_trace_file(path)
        if stats:
            print(f"  {label:<12} => Sent:{stats['sent']:>5} | Recv:{stats['received']:>5} | "
                  f"Drop:{stats['dropped']:>4} | PDR:{stats['pdr']:>6.2f}%")
            results[label] = stats
    return results


if __name__ == "__main__":
    run_ns2_simulation(BASELINE_SCRIPT)
    run_ns2_simulation(AI_SCRIPT)
    run_ns2_simulation(DQN_SCRIPT)
    compare_traces()
