# user_flow_simulation.py
import random
import csv
import statistics
import os
import sys

from registration import run_registration
from authentication import run_authentication
from matching import run_matching

# Safe import for matplotlib
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Plots will be skipped.", file=sys.stderr)

# === Global parameters (use exactly) ===
NUM_STUDENTS = 500
NUM_PEER_COUNSELORS = 30
PEAK_MULTIPLIER = 2.5
AVG_RESPONSE_TIME = 5  # minutes (proxy)
BURNOUT_THRESHOLD = 20  # sessions
TRUST_LEVEL = 0.85

SEEDS = [42, 43, 44, 45, 46]
SCENARIOS = {
    'Baseline': {'name':'Baseline','num_students': NUM_STUDENTS, 'num_peer_counselors': NUM_PEER_COUNSELORS, 'trust_level': TRUST_LEVEL},
    'MidtermStress': {'name':'MidtermStress','num_students': int(NUM_STUDENTS * PEAK_MULTIPLIER), 'num_peer_counselors': NUM_PEER_COUNSELORS, 'trust_level': TRUST_LEVEL},
    'CounselorShortage': {'name':'CounselorShortage','num_students': NUM_STUDENTS, 'num_peer_counselors': max(1, int(NUM_PEER_COUNSELORS * 0.6)), 'trust_level': TRUST_LEVEL},
    'TrustCollapse': {'name':'TrustCollapse','num_students': NUM_STUDENTS, 'num_peer_counselors': NUM_PEER_COUNSELORS, 'trust_level': max(0.0, TRUST_LEVEL - 0.25)}
}

OUT_DIR = "simulation_outputs"
os.makedirs(OUT_DIR, exist_ok=True)

def simulate_user_flow(params, seed, registration_failure_rate=0.0):
    random.seed(seed)
    registered, num_registered, num_reg_failed = run_registration(params['num_students'], registration_failure_rate)
    authenticated, num_login_success, num_login_failed = run_authentication(registered, params['trust_level'])
    matched, unmatched, loads, num_burned, avg_load, est_rt = run_matching(authenticated, params['num_peer_counselors'], BURNOUT_THRESHOLD, AVG_RESPONSE_TIME)
    # Validations
    if not (num_registered + num_reg_failed == params['num_students']):
        raise AssertionError(f"Registration counts mismatch: {params['name']} seed {seed}")
    if not (num_login_success + num_login_failed == num_registered):
        raise AssertionError(f"Authentication counts mismatch: {params['name']} seed {seed}")
    if not (matched + unmatched == num_login_success):
        raise AssertionError(f"Matching counts mismatch: {params['name']} seed {seed}")
    if not (num_burned <= params['num_peer_counselors']):
        raise AssertionError(f"Burned out > counselors: {params['name']} seed {seed}")
    return {
        'Scenario': params['name'],
        'Seed': seed,
        'NumStudents': params['num_students'],
        'NumRegistered': num_registered,
        'NumLoginSuccess': num_login_success,
        'NumLoginFailed': num_login_failed,
        'Matched': matched,
        'Unmatched': unmatched,
        'MatchedRate': matched / max(1, params['num_students']),
        'AvgCounselorLoad': avg_load,
        'NumBurnedOut': num_burned,
        'EstResponseTime': est_rt,
        'Loads': loads
    }

def main():
    scenario_csv = os.path.join(OUT_DIR, "scenario_table.csv")
    summary_csv = os.path.join(OUT_DIR, "summary_table.csv")
    with open(scenario_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Scenario','Seed','NumStudents','NumRegistered','NumLoginSuccess','NumLoginFailed','Matched','Unmatched','MatchedRate','AvgCounselorLoad','NumBurnedOut','EstResponseTime'])
    summary = {}
    for scenario_name, params in SCENARIOS.items():
        per_seed = []
        all_loads = []
        for seed in SEEDS:
            result = simulate_user_flow(params, seed)
            with open(scenario_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    result['Scenario'], result['Seed'], result['NumStudents'], result['NumRegistered'],
                    result['NumLoginSuccess'], result['NumLoginFailed'], result['Matched'], result['Unmatched'],
                    round(result['MatchedRate'],4), round(result['AvgCounselorLoad'],3), result['NumBurnedOut'], round(result['EstResponseTime'],3)
                ])
            per_seed.append(result)
            all_loads.extend(result['Loads'])
        # summary stats
        mr_mean = statistics.mean([r['MatchedRate'] for r in per_seed])
        mr_std = statistics.pstdev([r['MatchedRate'] for r in per_seed])
        nb_mean = statistics.mean([r['NumBurnedOut'] for r in per_seed])
        nb_std = statistics.pstdev([r['NumBurnedOut'] for r in per_seed])
        al_mean = statistics.mean([r['AvgCounselorLoad'] for r in per_seed])
        al_std = statistics.pstdev([r['AvgCounselorLoad'] for r in per_seed])
        rt_mean = statistics.mean([r['EstResponseTime'] for r in per_seed])
        rt_std = statistics.pstdev([r['EstResponseTime'] for r in per_seed])
        summary[scenario_name] = (mr_mean, mr_std, nb_mean, nb_std, al_mean, al_std, rt_mean, rt_std)
        # plots
        if HAS_MATPLOTLIB:
            mean_matched = statistics.mean([r['Matched'] for r in per_seed])
            mean_unmatched = statistics.mean([r['Unmatched'] for r in per_seed])
            plt.figure(figsize=(6,4))
            plt.bar(['Matched','Unmatched'], [mean_matched, mean_unmatched], color=['#4CAF50','#F44336'])
            plt.title(f"Matched vs Unmatched - {scenario_name}")
            plt.ylabel("Students (mean across seeds)")
            plt.savefig(os.path.join(OUT_DIR, f"matched_vs_unmatched_{scenario_name}.png"))
            plt.close()
            max_load = max(all_loads) if all_loads else 1
            bins = range(0, max_load + 2)
            plt.figure(figsize=(6,4))
            plt.hist(all_loads, bins=bins, color='#2196F3', edgecolor='black')
            plt.title(f"Counselor Workload Distribution - {scenario_name}")
            plt.xlabel("Sessions completed")
            plt.ylabel("Count (aggregated across seeds)")
            plt.savefig(os.path.join(OUT_DIR, f"counselor_workload_{scenario_name}.png"))
            plt.close()
        else:
            with open(os.path.join(OUT_DIR, f"plots_skipped_{scenario_name}.txt"), 'w', encoding='utf-8') as fh:
                fh.write("matplotlib not installed; plots skipped for this scenario.\n")
    # write summary CSV
    with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Scenario','MatchedRate_mean','MatchedRate_std','NumBurned_mean','NumBurned_std','AvgLoad_mean','AvgLoad_std','EstRT_mean','EstRT_std'])
        for s, vals in summary.items():
            writer.writerow([s, round(vals[0],4), round(vals[1],4), round(vals[2],3), round(vals[3],3), round(vals[4],3), round(vals[5],3), round(vals[6],3), round(vals[7],3)])
    print("Simulation complete. Outputs in:", OUT_DIR)

if __name__ == "__main__":
    main()
