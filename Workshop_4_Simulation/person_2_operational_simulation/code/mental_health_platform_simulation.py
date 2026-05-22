"""
============================================================
Workshop #4: System Simulation and Validation
Course:  Systems Analysis & Design
University: Universidad Distrital Francisco José de Caldas

Title:  Student Mental Health Support Platform — DES Simulation
Role:   Persona 2 — Process-Oriented Simulation
        (Appointment Scheduling & Queue Management)

Methodology: Discrete-Event Simulation (DES) with SimPy
Python dependencies: simpy, numpy, pandas, matplotlib

Run:  python mental_health_platform_simulation.py
Outputs: chart1_avg_wait_time.png
         chart2_counselor_utilisation.png
         chart3_dropout_and_sla.png   (bonus)
============================================================
"""

import simpy
import random
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # headless backend — no GUI required
import matplotlib.pyplot as plt


# =============================================================================
# SECTION 0 — GLOBAL SYSTEM CONSTANTS
# Fixed by project specification. Do not modify.
# =============================================================================
NUM_STUDENTS            = 500    # Total student population modeled per run
NUM_PEER_COUNSELORS     = 30     # Baseline counsellor pool size
AVG_SESSION_DURATION    = 30.0   # Minutes  — Normal distribution mean (μ)
SESSION_STD_DEV         = 5.0    # Minutes  — Normal distribution std-dev (σ)
MAX_WAITING_TIME        = 15.0   # Minutes  — SLA threshold for acceptable wait
PEAK_MULTIPLIER         = 2.5    # Arrival-rate multiplier for stress scenarios
RANDOM_SEED             = 42     # Global RNG seed for full reproducibility


# =============================================================================
# SECTION 1 — SIMPY PROCESS: STUDENT ENTITY
# Models the complete lifecycle of one student through the support system.
# =============================================================================
def student_process(env, sid, counselors, wait_times, dropouts, served,
                    abandonment_prob, patience_limit):
    """
    DES process representing a single student entity.

    Parameters
    ----------
    env              : simpy.Environment — shared simulation clock
    sid              : int               — unique student identifier
    counselors       : simpy.Resource    — shared counsellor pool (M/M/c queue)
    wait_times       : list              — collector for measured wait times
    dropouts         : list[int]         — mutable counter [baulks + reneges]
    served           : list[int]         — mutable counter [completed sessions]
    abandonment_prob : float             — probability of baulking at arrival
    patience_limit   : float | None      — max minutes willing to wait in queue
    """

    # STEP 1 — Baulking: student decides whether to attempt the queue at all.
    # Applied in Midterm Stress scenario: 5% of students give up before joining.
    if abandonment_prob > 0.0 and patience_limit is None:
        if random.random() < abandonment_prob:
            dropouts[0] += 1
            return  # student never enters the queue

    # STEP 2 — Queue: student requests an available counsellor slot.
    arrival_time = env.now
    with counselors.request() as req:

        if patience_limit is not None:
            # Trust Collapse mode: student reneges if not served within
            # patience_limit minutes (models erosion of institutional trust).
            result = yield req | env.timeout(patience_limit)
            if req not in result:
                dropouts[0] += 1
                return  # timeout fired — student leaves without service
        else:
            # Unlimited patience: student waits as long as necessary.
            yield req

        # STEP 3 — Service: counsellor session (Normal dist., minimum 1 min).
        wait_time = env.now - arrival_time
        wait_times.append(wait_time)

        session_duration = max(
            1.0, random.gauss(AVG_SESSION_DURATION, SESSION_STD_DEV)
        )
        yield env.timeout(session_duration)
        served[0] += 1  # session completed successfully


# =============================================================================
# SECTION 2 — SIMPY PROCESS: UTILISATION MONITOR
# Periodically samples the fraction of counsellors currently busy.
# =============================================================================
def utilisation_monitor(env, counselors, num_counselors, util_samples,
                         sim_end, interval=10.0):
    """
    Background process that records instantaneous counsellor utilisation (%).
    Terminates once simulated time exceeds sim_end (prevents infinite loop).
    """
    while env.now < sim_end:
        busy = counselors.count                          # currently occupied slots
        util_samples.append(100.0 * busy / num_counselors)
        yield env.timeout(interval)


# =============================================================================
# SECTION 3 — SIMPY PROCESS: ARRIVAL GENERATOR
# Generates NUM_STUDENTS student entities with Exponential inter-arrival times,
# modelling a Poisson arrival process as required by the specification.
# =============================================================================
def arrival_generator(env, counselors, wait_times, dropouts, served,
                       inter_arrival, abandonment_prob, patience_limit):
    """
    Poisson arrival generator: inter-arrival gaps ~ Exp(1 / inter_arrival).
    Each arrival spawns an independent student_process coroutine.
    """
    for sid in range(NUM_STUDENTS):
        env.process(student_process(
            env, sid, counselors, wait_times, dropouts, served,
            abandonment_prob, patience_limit
        ))
        # Exponentially distributed gap to the next arrival
        yield env.timeout(random.expovariate(1.0 / inter_arrival))


# =============================================================================
# SECTION 4 — SCENARIO RUNNER
# Initialises and executes one complete SimPy simulation for a given scenario.
# =============================================================================
def run_scenario(name, inter_arrival, num_counselors,
                 abandonment_prob=0.0, patience_limit=None, seed=RANDOM_SEED):
    """
    Execute one simulation scenario and return a results dictionary.

    Parameters
    ----------
    name             : str            — human-readable scenario label
    inter_arrival    : float          — mean minutes between student arrivals
    num_counselors   : int            — size of the counsellor resource pool
    abandonment_prob : float          — per-student baulking probability [0, 1]
    patience_limit   : float | None   — max wait before reneging (None = inf)
    seed             : int            — RNG seed for reproducibility

    Returns
    -------
    dict — keys: name, avg_wait, avg_util, dropouts, total,
                 served, pct_exceeded, dropout_rate
    """
    # Seed both RNGs for full reproducibility across runs
    random.seed(seed)
    np.random.seed(seed)

    # Initialise the SimPy environment and the shared M/M/c counsellor resource
    env        = simpy.Environment()
    counselors = simpy.Resource(env, capacity=num_counselors)

    # Mutable collectors (lists used as pass-by-reference containers)
    wait_times   = []
    dropouts     = [0]   # [total dropout count]
    served       = [0]   # [total served count]
    util_samples = []

    # Generous upper bound on simulation duration for the monitor's stop check
    sim_end = inter_arrival * 700

    # Register all processes with the SimPy engine
    env.process(arrival_generator(
        env, counselors, wait_times, dropouts, served,
        inter_arrival, abandonment_prob, patience_limit
    ))
    env.process(utilisation_monitor(
        env, counselors, num_counselors, util_samples, sim_end
    ))

    # Run the simulation to completion (all events consumed)
    env.run()

    # Compute derived metrics
    wt           = wait_times
    n_drop       = dropouts[0]
    n_serve      = served[0]
    avg_wait     = float(np.mean(wt)) if wt else 0.0
    avg_util     = float(np.mean(util_samples)) if util_samples else 0.0
    pct_exceeded = (
        100.0 * sum(1 for w in wt if w > MAX_WAITING_TIME) / len(wt)
        if wt else 0.0
    )
    dropout_rate = 100.0 * n_drop / NUM_STUDENTS if NUM_STUDENTS > 0 else 0.0



    return {
        "name":         name,
        "avg_wait":     avg_wait,
        "avg_util":     avg_util,
        "dropouts":     n_drop,
        "total":        NUM_STUDENTS,
        "served":       n_serve,
        "pct_exceeded": pct_exceeded,
        "dropout_rate": dropout_rate,
    }


# =============================================================================
# SECTION 5 — SCENARIO DEFINITIONS  (project-specified parameters)
# =============================================================================
SCENARIO_CONFIGS = [
    # Scenario 1 — Baseline
    # Normal operations. 1 student / 20 min; 30 counsellors; no abandonment.
    dict(
        name             = "1. Baseline",
        inter_arrival    = 20.0,
        num_counselors   = NUM_PEER_COUNSELORS,   # 30
        abandonment_prob = 0.0,
        patience_limit   = None,
    ),
    # Scenario 2 — Midterm / Finals Stress
    # PEAK_MULTIPLIER = 2.5 → effective inter-arrival = 20 / 2.5 = 8 min.
    # 5 % of students baulk before entering the queue.
    dict(
        name             = "2. Midterm Stress",
        inter_arrival    = 20.0 / PEAK_MULTIPLIER,   # 8.0 min
        num_counselors   = NUM_PEER_COUNSELORS,
        abandonment_prob = 0.05,
        patience_limit   = None,
    ),
    # Scenario 3 — Counsellor Shortage
    # Arrival rate unchanged; pool cut to 10. Isolates capacity effect.
    dict(
        name             = "3. Counselor Shortage",
        inter_arrival    = 20.0,
        num_counselors   = 10,                        # reduced pool
        abandonment_prob = 0.0,
        patience_limit   = None,
    ),
    # Scenario 4 — Trust Collapse
    # 1 student / 15 min. Students renege after 5 min of waiting.
    dict(
        name             = "4. Trust Collapse",
        inter_arrival    = 15.0,
        num_counselors   = NUM_PEER_COUNSELORS,
        abandonment_prob = 0.0,
        patience_limit   = 5.0,   # renege threshold (minutes)
    ),
]


# =============================================================================
# SECTION 6 — CHART HELPERS
# =============================================================================
# Shared dark-mode style for all charts
_CHART_STYLE = {
    "figure.facecolor": "#0d1117",
    "axes.facecolor":   "#161b22",
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  "#c9d1d9",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "text.color":       "#c9d1d9",
    "grid.color":       "#21262d",
    "grid.linestyle":   "--",
    "grid.alpha":        0.7,
}
# One distinct colour per scenario
_PALETTE = ["#58a6ff", "#f85149", "#e3b341", "#3fb950"]
_SHORT_LABELS = ["Baseline", "Midterm\nStress", "Counselor\nShortage", "Trust\nCollapse"]


def _bar_labels(ax, bars, values, suffix="", fontsize=12):
    """Annotate a bar chart with value labels above each bar."""
    for b, v in zip(bars, values):
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + max(abs(b.get_height()) * 0.03, 0.05),
            f"{v:.2f}{suffix}",
            ha="center", va="bottom",
            fontsize=fontsize, fontweight="bold", color="#ffffff"
        )


def plot_avg_wait(results, path="chart1_avg_wait_time.png"):
    """Chart 1 — Average waiting time across the four scenarios."""
    waits = [r["avg_wait"] for r in results]
    drops = [r["dropouts"] for r in results]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor("#0d1117")

    bars = ax.bar(_SHORT_LABELS, waits, color=_PALETTE, width=0.52,
                  edgecolor="#ffffff18", linewidth=0.9, zorder=3)
    ax.axhline(MAX_WAITING_TIME, color="#f85149", lw=2.0, ls="--", zorder=4,
               label=f"SLA Threshold — {int(MAX_WAITING_TIME)} min")
    _bar_labels(ax, bars, waits, suffix=" min")

    ax.set_title(
        "Average Student Waiting Time per Scenario\n"
        "Student Mental Health Support Platform — Universidad Distrital",
        fontsize=14, fontweight="bold", pad=14
    )
    ax.set_ylabel("Average Wait Time (minutes)", fontsize=12, labelpad=10)
    ax.set_xlabel("Operational Scenario", fontsize=12, labelpad=8)
    ax.set_ylim(0, max(waits) * 1.7 + 3 if max(waits) > 0 else 20)
    ax.grid(axis="y", zorder=0)
    ax.legend(fontsize=10, facecolor="#161b22", edgecolor="#30363d")

    info = "\n".join([
        f"Dropouts — {_SHORT_LABELS[i].replace(chr(10), ' ')}: {drops[i]}"
        for i in range(4)
    ])
    ax.text(0.99, 0.97, info, transform=ax.transAxes, fontsize=9,
            va="top", ha="right",
            bbox=dict(fc="#161b22", ec="#30363d", boxstyle="round,pad=0.5"),
            color="#8b949e")

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_utilisation(results, path="chart2_counselor_utilisation.png"):
    """Chart 2 — Counsellor utilisation rate across the four scenarios."""
    utils = [r["avg_util"] for r in results]
    srvd  = [r["served"]   for r in results]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor("#0d1117")

    bars = ax.bar(_SHORT_LABELS, utils, color=_PALETTE, width=0.52,
                  edgecolor="#ffffff18", linewidth=0.9, zorder=3)
    ax.axhline(90,  color="#e3b341", lw=2.0, ls="--", zorder=4,
               label="Overload Threshold (90 %)")
    ax.axhline(100, color="#f85149", lw=1.5, ls=":",  zorder=4,
               label="Full Capacity (100 %)")
    _bar_labels(ax, bars, utils, suffix="%")

    ax.set_title(
        "Peer Counsellor Utilisation Rate per Scenario\n"
        "Student Mental Health Support Platform — Universidad Distrital",
        fontsize=14, fontweight="bold", pad=14
    )
    ax.set_ylabel("Average Utilisation (%)", fontsize=12, labelpad=10)
    ax.set_xlabel("Operational Scenario", fontsize=12, labelpad=8)
    ax.set_ylim(0, 115)
    ax.grid(axis="y", zorder=0)
    ax.legend(fontsize=10, facecolor="#161b22", edgecolor="#30363d")

    sv = "\n".join([
        f"Served — {_SHORT_LABELS[i].replace(chr(10), ' ')}: {srvd[i]}"
        for i in range(4)
    ])
    ax.text(0.02, 0.97, sv, transform=ax.transAxes, fontsize=9,
            va="top", ha="left",
            bbox=dict(fc="#161b22", ec="#30363d", boxstyle="round,pad=0.5"),
            color="#8b949e")

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_dropout_sla(results, path="chart3_dropout_and_sla.png"):
    """Chart 3 (bonus) — Dropout rate vs SLA wait-time violation rate."""
    drop_pct = [r["dropout_rate"] for r in results]
    exceeded = [r["pct_exceeded"] for r in results]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor("#0d1117")
    x, w = np.arange(4), 0.34

    b1 = ax.bar(x - w/2, drop_pct, w, color=_PALETTE,
                edgecolor="#ffffff18", zorder=3, label="Dropout Rate (%)")
    b2 = ax.bar(x + w/2, exceeded, w,
                color=[c + "88" for c in _PALETTE],
                edgecolor="#ffffff18", zorder=3, hatch="///",
                label=f"Wait > {int(MAX_WAITING_TIME)} min (%)")

    for b, v in zip(b1, drop_pct):
        if v > 0:
            ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.1,
                    f"{v:.1f}%", ha="center", fontsize=10,
                    color="#ffffff", fontweight="bold")
    for b, v in zip(b2, exceeded):
        if v > 0:
            ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.1,
                    f"{v:.1f}%", ha="center", fontsize=10,
                    color="#ffffff", fontweight="bold")

    ax.set_title(
        "Dropout Rate vs. SLA Wait-Time Violation Rate per Scenario\n"
        "Student Mental Health Support Platform — Universidad Distrital",
        fontsize=14, fontweight="bold", pad=14
    )
    ax.set_ylabel("Percentage (%)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(_SHORT_LABELS)
    ymax = max(max(drop_pct), max(exceeded)) * 1.4 + 1
    ax.set_ylim(0, max(ymax, 8))
    ax.grid(axis="y", zorder=0)
    ax.legend(fontsize=10, facecolor="#161b22", edgecolor="#30363d")

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


# =============================================================================
# SECTION 7 — MAIN ENTRY POINT
# =============================================================================
def main():
    # Apply chart style globally
    plt.rcParams.update(_CHART_STYLE)

    # ── Run all four scenarios ──────────────────────────────────────────────
    results = [run_scenario(**cfg) for cfg in SCENARIO_CONFIGS]

    # ── Print console summary table ─────────────────────────────────────────
    df = pd.DataFrame(results)[
        ["name", "avg_wait", "avg_util", "dropouts",
         "dropout_rate", "served", "pct_exceeded"]
    ]
    df.columns = [
        "Scenario", "Avg Wait (min)", "Util (%)",
        "Dropouts (#)", "Dropout (%)", "Served", "Wait>15min (%)"
    ]
    print("\n" + "=" * 80)
    print("  SIMULATION RESULTS — SUMMARY TABLE")
    print("=" * 80)
    print(df.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print("=" * 80 + "\n")

    # ── Generate and save visualisations ────────────────────────────────────
    plot_avg_wait(results)
    plot_utilisation(results)
    plot_dropout_sla(results)


if __name__ == "__main__":
    main()