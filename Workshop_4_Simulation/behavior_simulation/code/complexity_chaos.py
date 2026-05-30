import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# ─────────────────────────────────────────────
# SHARED GLOBAL PARAMETERS
# ─────────────────────────────────────────────
NUM_STUDENTS        = 500
NUM_PEER_COUNSELORS = 30
PEAK_MULTIPLIER     = 2.5
AVG_RESPONSE_TIME   = 5
BURNOUT_THRESHOLD   = 20
TRUST_LEVEL         = 0.85

np.random.seed(42)
SIM_WEEKS           = 16
TRUST_RECOVERY_RATE = 0.03
BURNOUT_RECOVERY    = 0.04

OUT_DIR = r"C:\Users\aliss\Documents\Python\outputs"
os.makedirs(OUT_DIR, exist_ok=True)

COLORS = {
    "baseline": "#2196F3",
    "midterm":  "#FF9800",
    "shortage": "#F44336",
    "trust":    "#9C27B0",
    "neutral":  "#607D8B",
    "positive": "#4CAF50",
    "danger":   "#E53935",
}
SCENARIO_KEYS   = ["baseline", "midterm", "shortage", "trust"]
SCENARIO_LABELS = [
    "Baseline Scenario",
    "Midterm/Finals Stress Scenario",
    "Counselor Shortage Scenario",
    "Trust Collapse Scenario",
]

# ═════════════════════════════════════════════
# FEEDBACK LOOP SIMULATION
# ═════════════════════════════════════════════

def simulate_feedback_loop(
    scenario: str,
    weeks: int = SIM_WEEKS,
    num_counselors: int = NUM_PEER_COUNSELORS,
    peak_mult: float = PEAK_MULTIPLIER,
    trust_init: float = TRUST_LEVEL,
) -> pd.DataFrame:
    """
    Weekly system dynamics model.

    Burnout logic:
        sessions_demanded = active * (SESSIONS_PER_WEEK / NUM_STUDENTS) * demand_mult
        max_capacity      = available_counselors * BURNOUT_THRESHOLD
        demand_ratio      = sessions_demanded / max_capacity
        burnout accumulates when demand_ratio > 0.70
        burnout_pressure  = max(0, demand_ratio - 0.70) / 0.30
        burnout += burnout_pressure * 0.08 - BURNOUT_RECOVERY

    Calibration target:
        baseline  demand_ratio ~0.51 → burnout stays 0   (safe)
        midterm   demand_ratio ~0.80 → burnout reaches ~0.45 by week 16
        shortage  demand_ratio ~0.97 → burnout reaches ~0.60 by week 16
        trust     demand_ratio ~0.51 → burnout stays 0; dropout rises from shock
    """

    SESSIONS_PER_WEEK = 300   # platform-wide weekly session capacity target

    trust      = trust_init
    counselors = num_counselors
    active     = int(NUM_STUDENTS * trust * 0.76)
    burnout    = 0.0
    quality    = 0.90

    if scenario == "baseline":
        demand_mult    = 1.0
        counselor_mult = 1.0
        trust_shock    = 0.0
        shock_week     = 99

    elif scenario == "midterm":
        demand_mult    = peak_mult          # 2.5x
        counselor_mult = 1.0
        trust_shock    = 0.0
        shock_week     = 99

    elif scenario == "shortage":
        demand_mult    = 1.0
        counselor_mult = 10 / NUM_PEER_COUNSELORS   # 10/30
        trust_shock    = 0.0
        shock_week     = 99

    elif scenario == "trust":
        demand_mult    = 1.0
        counselor_mult = 1.0
        trust_shock    = 0.40
        shock_week     = 4

    records = []

    for week in range(1, weeks + 1):

        available    = max(1, int(counselors * counselor_mult))
        max_capacity = available * BURNOUT_THRESHOLD

        sessions_demanded = int(
            active * (SESSIONS_PER_WEEK / NUM_STUDENTS) * demand_mult
        )
        sessions_served = min(sessions_demanded, max_capacity)

        # Burnout: activates when demand exceeds 70% of capacity
        demand_ratio     = sessions_demanded / max(1, max_capacity)
        burnout_pressure = max(0.0, (demand_ratio - 0.70) / 0.30)
        burnout = min(1.0, burnout + burnout_pressure * 0.08 - BURNOUT_RECOVERY)
        burnout = max(0.0, burnout)

        # Quality degrades with burnout
        quality = max(0.4, quality - burnout * 0.05 + (1 - burnout) * 0.015)
        quality = min(1.0, quality)

        # Trust shock
        if week == shock_week:
            trust = max(0.0, trust - trust_shock)

        # Trust recovery
        unmet_ratio = max(0.0, (sessions_demanded - max_capacity)
                          / max(1, sessions_demanded))
        trust_delta = (TRUST_RECOVERY_RATE * quality
                       - burnout * 0.03
                       - unmet_ratio * 0.04)
        trust = max(0.0, min(1.0, trust + trust_delta))

        # Dropout
        dropout_rate = max(
            0.0,
            (1 - quality) * 0.6 * 0.12
            + (1 - trust)  * 0.6 * 0.08
        )
        dropouts = int(active * dropout_rate)

        # New arrivals gated by counselor availability
        counselor_ratio = available / NUM_PEER_COUNSELORS
        new_arrivals = int(
            (NUM_STUDENTS - active) * trust * quality * counselor_ratio * 0.07
        )
        active = max(0, min(NUM_STUDENTS, active - dropouts + new_arrivals))

        records.append({
            "week":            week,
            "trust_level":     round(trust,        4),
            "active_students": active,
            "counselor_load":  round(sessions_served / max(1, available), 2),
            "burnout_index":   round(burnout,       4),
            "dropout_rate":    round(dropout_rate,  4),
            "quality_index":   round(quality,       4),
            "sessions_served": sessions_served,
            "unmet_demand":    max(0, sessions_demanded - max_capacity),
            "demand_ratio":    round(demand_ratio,  4),
        })

    return pd.DataFrame(records)


# ═════════════════════════════════════════════
# SENSITIVITY ANALYSIS
# ═════════════════════════════════════════════

def sensitivity_analysis() -> dict:
    results = {}

    # Trust Level sweep (baseline scenario)
    trust_rows = []
    for tv in np.linspace(0.30, 1.0, 20):
        df = simulate_feedback_loop("baseline", trust_init=tv)
        trust_rows.append({
            "parameter_value": tv,
            "final_trust":   df["trust_level"].iloc[-1],
            "final_burnout": df["burnout_index"].iloc[-1],
            "avg_dropout":   df["dropout_rate"].mean(),
            "avg_active":    df["active_students"].mean(),
        })
    results["trust"] = pd.DataFrame(trust_rows)

    # Counselor count sweep (midterm scenario — shows burnout variation)
    counselor_rows = []
    for cv in range(5, 51, 5):
        df = simulate_feedback_loop("midterm", num_counselors=cv)
        counselor_rows.append({
            "parameter_value": cv,
            "final_trust":   df["trust_level"].iloc[-1],
            "final_burnout": df["burnout_index"].iloc[-1],
            "avg_dropout":   df["dropout_rate"].mean(),
            "avg_active":    df["active_students"].mean(),
        })
    results["counselors"] = pd.DataFrame(counselor_rows)

    # Peak multiplier sweep (midterm scenario)
    peak_rows = []
    for pm in np.linspace(1.0, 4.0, 16):
        df = simulate_feedback_loop("midterm", peak_mult=pm)
        peak_rows.append({
            "parameter_value": pm,
            "final_trust":   df["trust_level"].iloc[-1],
            "final_burnout": df["burnout_index"].iloc[-1],
            "avg_dropout":   df["dropout_rate"].mean(),
            "avg_active":    df["active_students"].mean(),
        })
    results["peak_mult"] = pd.DataFrame(peak_rows)

    return results


# ═════════════════════════════════════════════
# EMERGENT BEHAVIOR MONTE CARLO
# ═════════════════════════════════════════════

def simulate_emergent_cascade(n_runs: int = 300) -> pd.DataFrame:
    rng  = np.random.default_rng(42)
    rows = []
    for scenario in SCENARIO_KEYS:
        stabilised   = 0
        collapsed    = 0
        avg_recovery = []
        p_trigger    = {"baseline": 0.05, "midterm": 0.25,
                        "shortage": 0.30, "trust":   0.55}[scenario]

        for _ in range(n_runs):
            trust   = TRUST_LEVEL
            burnout = 0.0
            weeks_to_recover = None

            for week in range(1, 25):
                if rng.random() < p_trigger:
                    trust   = max(0.0, trust   - rng.uniform(0.05, 0.20))
                    burnout = min(1.0, burnout  + rng.uniform(0.05, 0.15))

                trust   = min(1.0, trust   + TRUST_RECOVERY_RATE * (1 - burnout))
                burnout = max(0.0, burnout - BURNOUT_RECOVERY)

                if trust < 0.35 and burnout > 0.60:
                    collapsed += 1
                    break
                if trust > 0.75 and burnout < 0.15 and week > 4:
                    stabilised += 1
                    if weeks_to_recover is None:
                        weeks_to_recover = week
                    break

            if weeks_to_recover:
                avg_recovery.append(weeks_to_recover)

        rows.append({
            "scenario":           scenario,
            "stabilised_pct":     round(stabilised / n_runs * 100, 1),
            "collapsed_pct":      round(collapsed  / n_runs * 100, 1),
            "partial_pct":        round((n_runs - stabilised - collapsed) / n_runs * 100, 1),
            "avg_weeks_recovery": round(np.mean(avg_recovery), 1) if avg_recovery else None,
        })
    return pd.DataFrame(rows)


# ═════════════════════════════════════════════
# FIGURE 1
# ═════════════════════════════════════════════

def plot_figure1(scenario_data: dict):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(
        "Figure 1. Trust Level and Burnout Index Over Time — All Scenarios\n"
        "Student Mental Health Support Platform — Universidad Distrital",
        fontsize=13, fontweight="bold", y=1.01,
    )
    ax_trust, ax_burn = axes

    for key, label in zip(SCENARIO_KEYS, SCENARIO_LABELS):
        df = scenario_data[key]
        ax_trust.plot(df["week"], df["trust_level"],
                      color=COLORS[key], linewidth=2.5, label=label)
        ax_burn.plot(df["week"],  df["burnout_index"],
                     color=COLORS[key], linewidth=2.5, label=label)

    ax_trust.axhline(TRUST_LEVEL, color="grey", linestyle="--", linewidth=1.2,
                     label=f"Baseline trust = {TRUST_LEVEL}")
    ax_trust.axhline(0.50, color="red", linestyle=":", linewidth=1.2,
                     label="Collapse threshold (0.50)")
    ax_trust.set_ylabel("Trust Level [0–1]", fontsize=11)
    ax_trust.set_ylim(0, 1.08)
    ax_trust.set_title("Trust Level Dynamics", fontsize=11)
    ax_trust.legend(fontsize=8, loc="lower right")
    ax_trust.grid(axis="y", alpha=0.3)

    ax_burn.axhline(0.40, color="orange", linestyle="--", linewidth=1.2,
                    label="Warning threshold (0.40)")
    ax_burn.axhline(0.70, color="red",    linestyle=":", linewidth=1.2,
                    label="Critical burnout (0.70)")
    ax_burn.set_ylabel("Burnout Index [0–1]", fontsize=11)
    ax_burn.set_xlabel("Simulation Week", fontsize=11)
    ax_burn.set_ylim(0, 1.08)
    ax_burn.set_title("Counselor Burnout Dynamics", fontsize=11)
    ax_burn.legend(fontsize=8, loc="upper left")
    ax_burn.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "figure1_feedback_loops.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ═════════════════════════════════════════════
# FIGURE 2
# ═════════════════════════════════════════════

def plot_figure2(scenario_data: dict):
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.suptitle(
        "Figure 2. Active Students and Weekly Dropout Rate by Scenario\n"
        "Student Mental Health Support Platform — Universidad Distrital",
        fontsize=13, fontweight="bold",
    )
    for ax, key, label in zip(axes.flat, SCENARIO_KEYS, SCENARIO_LABELS):
        df  = scenario_data[key]
        c   = COLORS[key]
        ax2 = ax.twinx()

        ax.bar(df["week"], df["active_students"], color=c, alpha=0.4,
               label="Active students")
        ax.set_ylabel("Active Students", fontsize=9, color=c)
        ax.set_ylim(0, NUM_STUDENTS * 1.1)
        ax.tick_params(axis="y", labelcolor=c)

        ax2.plot(df["week"], df["dropout_rate"] * 100,
                 color=COLORS["danger"], linewidth=2, label="Dropout rate (%)")
        ax2.set_ylabel("Dropout Rate (%)", fontsize=9, color=COLORS["danger"])
        ax2.set_ylim(0, 25)
        ax2.tick_params(axis="y", labelcolor=COLORS["danger"])

        ax.set_title(label, fontsize=10, fontweight="bold")
        ax.set_xlabel("Week", fontsize=9)
        ax.grid(axis="y", alpha=0.2)

        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, fontsize=7, loc="upper right")

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "figure2_active_students_dropout.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ═════════════════════════════════════════════
# FIGURE 3
# ═════════════════════════════════════════════

def plot_figure3(sensitivity_data: dict):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        "Figure 3. Sensitivity Analysis — Impact of Key Parameters on System Stability\n"
        "Student Mental Health Support Platform — Universidad Distrital",
        fontsize=13, fontweight="bold",
    )

    # Left: Trust Level
    ax = axes[0]
    df = sensitivity_data["trust"]
    ax.plot(df["parameter_value"], df["final_trust"],
            color=COLORS["baseline"], linewidth=2.2, label="Final Trust")
    ax.plot(df["parameter_value"], df["final_burnout"],
            color=COLORS["midterm"], linewidth=2.2, linestyle="--",
            label="Final Burnout")
    ax.axvline(0.85, color="grey", linestyle=":", linewidth=1.2,
               label="Baseline (0.85)")
    ax.axvline(0.50, color="red",  linestyle=":", linewidth=1.2,
               label="Collapse threshold")
    ax.set_xlabel("Initial Trust Level", fontsize=10)
    ax.set_ylabel("Final Value [0–1]", fontsize=10)
    ax.set_title("Sensitivity to Initial Trust Level\n(Baseline Scenario)", fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 1.1)

    # Center: Counselor count (Midterm) — shows burnout vs active students
    ax  = axes[1]
    df  = sensitivity_data["counselors"]
    ax2 = ax.twinx()
    ax.plot(df["parameter_value"], df["avg_active"],
            color=COLORS["positive"], linewidth=2.2, label="Avg Active Students")
    ax2.plot(df["parameter_value"], df["final_burnout"],
             color=COLORS["danger"], linewidth=2.2, linestyle="--",
             label="Final Burnout")
    ax.axvline(30, color="grey", linestyle=":", linewidth=1.2, label="Baseline (30)")
    ax.axvline(10, color="red",  linestyle=":", linewidth=1.2, label="Shortage (10)")
    ax.set_xlabel("Number of Peer Counselors", fontsize=10)
    ax.set_ylabel("Avg Active Students", fontsize=10, color=COLORS["positive"])
    ax.tick_params(axis="y", labelcolor=COLORS["positive"])
    ax2.set_ylabel("Burnout Index [0–1]", fontsize=9, color=COLORS["danger"])
    ax2.tick_params(axis="y", labelcolor=COLORS["danger"])
    ax2.set_ylim(0, 1.1)
    ax.set_title("Sensitivity to Peer Counselor Count\n(Midterm Stress Scenario)", fontsize=10)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7, loc="center right")
    ax.grid(alpha=0.3)

    # Right: Peak multiplier
    ax = axes[2]
    df = sensitivity_data["peak_mult"]
    ax.plot(df["parameter_value"], df["final_burnout"],
            color=COLORS["shortage"], linewidth=2.2, label="Final Burnout")
    ax.plot(df["parameter_value"], df["avg_dropout"],
            color=COLORS["trust"], linewidth=2.2, linestyle="--",
            label="Avg Dropout Rate")
    ax.axvline(PEAK_MULTIPLIER, color="grey",   linestyle=":", linewidth=1.2,
               label=f"PEAK_MULTIPLIER ({PEAK_MULTIPLIER})")
    ax.axvline(2.0, color="orange", linestyle=":", linewidth=1.2,
               label="Dropout onset (~2.0×)")
    ax.set_xlabel("Peak Demand Multiplier", fontsize=10)
    ax.set_ylabel("Index / Rate [0–1]", fontsize=10)
    ax.set_title("Sensitivity to Peak Demand Multiplier\n(Midterm/Finals Scenario)", fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 1.1)

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "figure3_sensitivity_analysis.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ═════════════════════════════════════════════
# FIGURE 4
# ═════════════════════════════════════════════

def plot_figure4(cascade_df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        "Figure 4. Emergent Behavior — Cascade Outcomes and Recovery Time\n"
        "Student Mental Health Support Platform — Universidad Distrital",
        fontsize=13, fontweight="bold",
    )
    x = np.arange(len(SCENARIO_LABELS))

    ax = axes[0]
    ax.bar(x, cascade_df["stabilised_pct"], color=COLORS["positive"],
           label="Stabilised (%)", width=0.5)
    ax.bar(x, cascade_df["collapsed_pct"],
           bottom=cascade_df["stabilised_pct"],
           color=COLORS["danger"], label="Collapsed (%)", width=0.5)
    ax.bar(x, cascade_df["partial_pct"],
           bottom=cascade_df["stabilised_pct"] + cascade_df["collapsed_pct"],
           color=COLORS["neutral"], label="Partial / Unresolved (%)", width=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(SCENARIO_LABELS, fontsize=8)
    ax.set_ylabel("Percentage of Monte Carlo Runs (%)", fontsize=10)
    ax.set_ylim(0, 115)
    ax.set_title("System Outcome Distribution (n=300 runs each)", fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    for i, row in cascade_df.iterrows():
        ax.text(i, row["stabilised_pct"] / 2,
                f"{row['stabilised_pct']}%", ha="center", va="center",
                fontsize=8, color="white", fontweight="bold")
        if row["collapsed_pct"] > 3:
            ax.text(i, row["stabilised_pct"] + row["collapsed_pct"] / 2,
                    f"{row['collapsed_pct']}%", ha="center", va="center",
                    fontsize=8, color="white", fontweight="bold")

    ax2 = axes[1]
    recovery   = cascade_df["avg_weeks_recovery"].fillna(0).values
    bar_colors = [COLORS[k] for k in SCENARIO_KEYS]
    bars       = ax2.bar(x, recovery, color=bar_colors, width=0.5, alpha=0.85)
    ax2.set_xticks(x)
    ax2.set_xticklabels(SCENARIO_LABELS, fontsize=8)
    ax2.set_ylabel("Average Weeks to Stabilise", fontsize=10)
    ax2.set_title("Average Recovery Time (Stabilised Runs)", fontsize=10)
    ax2.set_ylim(0, max(recovery) * 1.4 + 1)
    ax2.grid(axis="y", alpha=0.3)
    for bar, val in zip(bars, recovery):
        if val > 0:
            ax2.text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.15,
                     f"{val:.1f} wk", ha="center", va="bottom",
                     fontsize=9, fontweight="bold")

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "figure4_emergent_behavior.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ═════════════════════════════════════════════
# SUMMARY TABLE
# ═════════════════════════════════════════════

def build_summary_table(scenario_data: dict, cascade_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key, label in zip(SCENARIO_KEYS, SCENARIO_LABELS):
        df   = scenario_data[key]
        crow = cascade_df[cascade_df["scenario"] == key].iloc[0]
        rows.append({
            "Scenario":             label,
            "Avg Trust Level":      f"{df['trust_level'].mean():.3f}",
            "Min Trust Level":      f"{df['trust_level'].min():.3f}",
            "Avg Burnout Index":    f"{df['burnout_index'].mean():.3f}",
            "Max Burnout Index":    f"{df['burnout_index'].max():.3f}",
            "Avg Active Students":  f"{df['active_students'].mean():.0f}",
            "Avg Dropout Rate (%)": f"{df['dropout_rate'].mean()*100:.2f}%",
            "Total Unmet Demand":   f"{df['unmet_demand'].sum():.0f}",
            "Stabilised Runs (%)":  f"{crow['stabilised_pct']}%",
            "Collapsed Runs (%)":   f"{crow['collapsed_pct']}%",
            "Avg Recovery (wk)":    (f"{crow['avg_weeks_recovery']:.1f}"
                                     if crow["avg_weeks_recovery"] else "N/A"),
        })
    return pd.DataFrame(rows)


# ═════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════

def main():
    print("=" * 60)
    print("Persona 4 — Complexity and Chaos Analysis (FINAL)")
    print("Student Mental Health Support Platform")
    print("=" * 60)

    print("\n[1/4] Running feedback-loop simulations...")
    scenario_data = {key: simulate_feedback_loop(key) for key in SCENARIO_KEYS}
    for key in SCENARIO_KEYS:
        df = scenario_data[key]
        print(f"  {key:10s} → max burnout={df['burnout_index'].max():.3f}  "
              f"min trust={df['trust_level'].min():.3f}  "
              f"avg active={df['active_students'].mean():.0f}")

    print("\n[2/4] Running sensitivity analysis...")
    sensitivity_data = sensitivity_analysis()

    print("[3/4] Running emergent cascade (n=300)...")
    cascade_df = simulate_emergent_cascade(n_runs=300)

    print("[4/4] Generating figures...")
    plot_figure1(scenario_data)
    plot_figure2(scenario_data)
    plot_figure3(sensitivity_data)
    plot_figure4(cascade_df)

    summary = build_summary_table(scenario_data, cascade_df)
    print("\n─── SUMMARY TABLE ───────────────────────────────────────")
    print(summary.to_string(index=False))

    csv_path = os.path.join(OUT_DIR, "persona4_summary_table.csv")
    summary.to_csv(csv_path, index=False)
    print(f"\nSaved: {csv_path}")

    print("\n─── EMERGENT CASCADE ────────────────────────────────────")
    print(cascade_df.to_string(index=False))
    print("\n✓ Done. Outputs saved to:", OUT_DIR)


if __name__ == "__main__":
    main()
