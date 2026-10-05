"""
Cricket Analytics System: Exploratory Data Analysis & Visualization Module
Generates publication-ready figures for portfolio, reports, and GitHub documentation.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")

# Configure modern, professional styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10
plt.rcParams["figure.titlesize"] = 14

PRIMARY_COLOR = "#1f77b4"
ACCENT_COLOR = "#ff7f0e"
SUCCESS_COLOR = "#2ca02c"
DANGER_COLOR = "#d62728"


def plot_top_batsmen(df_bat, save_dir=REPORTS_DIR):
    """Plot Top 10 all-time run scorers with strike rate annotation."""
    plt.figure(figsize=(10, 6), dpi=300)
    top10 = df_bat.head(10).sort_values(by="runs", ascending=True)

    colors = ["#1f77b4" if r < top10["runs"].max() else "#d62728" for r in top10["runs"]]
    bars = plt.barh(top10["player_name"], top10["runs"], color=colors, edgecolor="black", alpha=0.85)

    for bar, sr, avg in zip(bars, top10["strike_rate"], top10["batting_average"]):
        w = bar.get_width()
        plt.text(w + 100, bar.get_y() + bar.get_height() / 2, f"{int(w):,} (SR: {sr} | Avg: {avg})",
                 va="center", ha="left", fontsize=9, fontweight="semibold")

    plt.title("All-Time Top 10 IPL Run Scorers (With Strike Rate & Batting Average)", pad=15)
    plt.xlabel("Total Runs Scored")
    plt.xlim(0, top10["runs"].max() * 1.25)
    plt.tight_layout()
    path = os.path.join(save_dir, "eda_01_top_run_scorers.png")
    plt.savefig(path)
    plt.close()
    print(f"[OK] Generated {path}")


def plot_top_bowlers(df_bowl, save_dir=REPORTS_DIR):
    """Plot Top 10 all-time wicket takers with economy annotation."""
    plt.figure(figsize=(10, 6), dpi=300)
    top10 = df_bowl.head(10).sort_values(by="wickets", ascending=True)

    colors = ["#2ca02c" if w < top10["wickets"].max() else "#9467bd" for w in top10["wickets"]]
    bars = plt.barh(top10["player_name"], top10["wickets"], color=colors, edgecolor="black", alpha=0.85)

    for bar, econ, dot_pct in zip(bars, top10["economy_rate"], top10["dot_ball_pct"]):
        w = bar.get_width()
        plt.text(w + 2, bar.get_y() + bar.get_height() / 2, f"{int(w)} wkts (Econ: {econ} | Dot: {dot_pct}%)",
                 va="center", ha="left", fontsize=9, fontweight="semibold")

    plt.title("All-Time Top 10 IPL Wicket Takers (With Economy & Dot Ball %)", pad=15)
    plt.xlabel("Total Wickets Taken")
    plt.xlim(0, top10["wickets"].max() * 1.25)
    plt.tight_layout()
    path = os.path.join(save_dir, "eda_02_top_wicket_takers.png")
    plt.savefig(path)
    plt.close()
    print(f"[OK] Generated {path}")


def plot_batting_quadrant(df_bat, save_dir=REPORTS_DIR):
    """Plot Batting Average vs Strike Rate (Quadrant Analysis for Min 1000 Runs)."""
    plt.figure(figsize=(10, 7), dpi=300)
    qual = df_bat[df_bat["runs"] >= 1000].copy()

    median_sr = qual["strike_rate"].median()
    median_avg = qual["batting_average"].median()

    sns.scatterplot(
        data=qual,
        x="strike_rate",
        y="batting_average",
        size="runs",
        sizes=(40, 400),
        hue="batting_impact",
        palette="viridis",
        alpha=0.8,
        edgecolor="black"
    )

    # Reference median lines
    plt.axvline(median_sr, color="gray", linestyle="--", alpha=0.7, label=f"Median SR ({median_sr:.1f})")
    plt.axhline(median_avg, color="gray", linestyle="--", alpha=0.7, label=f"Median Avg ({median_avg:.1f})")

    # Annotate top stars
    notable = ["V Kohli", "MS Dhoni", "AB de Villiers", "CH Gayle", "DA Warner", "SK Raina", "RG Sharma", "KL Rahul", "AD Russell"]
    for _, row in qual[qual["player_name"].isin(notable)].iterrows():
        plt.annotate(
            row["player_name"],
            xy=(row["strike_rate"], row["batting_average"]),
            xytext=(row["strike_rate"] + 1.2, row["batting_average"] + 0.6),
            fontsize=9,
            fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="black", lw=0.8)
        )

    plt.title("Batting Quadrant Analysis: Strike Rate vs Batting Average (Min 1,000 Runs)", pad=15)
    plt.xlabel("Career Strike Rate (Runs / 100 Balls)")
    plt.ylabel("Career Batting Average")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    plt.tight_layout()
    path = os.path.join(save_dir, "eda_03_batting_quadrant.png")
    plt.savefig(path)
    plt.close()
    print(f"[OK] Generated {path}")


def plot_bowling_quadrant(df_bowl, save_dir=REPORTS_DIR):
    """Plot Bowling Economy vs Bowling Strike Rate (Min 50 Wickets)."""
    plt.figure(figsize=(10, 7), dpi=300)
    qual = df_bowl[df_bowl["wickets"] >= 50].copy()

    med_econ = qual["economy_rate"].median()
    med_sr = qual["bowling_strike_rate"].median()

    sns.scatterplot(
        data=qual,
        x="economy_rate",
        y="bowling_strike_rate",
        size="wickets",
        sizes=(40, 400),
        hue="bowling_impact",
        palette="flare",
        alpha=0.8,
        edgecolor="black"
    )

    plt.axvline(med_econ, color="gray", linestyle="--", alpha=0.7, label=f"Median Econ ({med_econ:.2f})")
    plt.axhline(med_sr, color="gray", linestyle="--", alpha=0.7, label=f"Median SR ({med_sr:.1f})")

    # Invert Y and X axes logically: lower economy & lower strike rate is top tier!
    notable = ["SL Malinga", "SP Narine", "JJ Bumrah", "YS Chahal", "Rashid Khan", "B Kumar", "DJ Bravo", "R Ashwin"]
    for _, row in qual[qual["player_name"].isin(notable)].iterrows():
        plt.annotate(
            row["player_name"],
            xy=(row["economy_rate"], row["bowling_strike_rate"]),
            xytext=(row["economy_rate"] + 0.1, row["bowling_strike_rate"] + 0.4),
            fontsize=9,
            fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="black", lw=0.8)
        )

    plt.title("Bowling Efficiency: Economy Rate vs Bowling Strike Rate (Min 50 Wickets)", pad=15)
    plt.xlabel("Career Economy Rate (Runs Conceded / Over) [Lower is Better]")
    plt.ylabel("Bowling Strike Rate (Balls / Wicket) [Lower is Better]")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    plt.tight_layout()
    path = os.path.join(save_dir, "eda_04_bowling_efficiency.png")
    plt.savefig(path)
    plt.close()
    print(f"[OK] Generated {path}")


def plot_team_win_pct(df_team, save_dir=REPORTS_DIR):
    """Plot Franchise Win Percentage (Min 20 Matches)."""
    plt.figure(figsize=(10, 6), dpi=300)
    active = df_team[df_team["matches_played"] >= 20].sort_values(by="win_pct", ascending=True)

    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(active)))
    bars = plt.barh(active["team_name"], active["win_pct"], color=colors, edgecolor="black")

    for bar, w, l in zip(bars, active["wins"], active["losses"]):
        width = bar.get_width()
        plt.text(width + 0.8, bar.get_y() + bar.get_height() / 2, f"{width:.1f}% ({w}W - {l}L)",
                 va="center", ha="left", fontsize=9, fontweight="semibold")

    plt.title("Franchise All-Time Win Percentage (Min 20 Matches Played)", pad=15)
    plt.xlabel("Win Percentage (%)")
    plt.xlim(0, 75)
    plt.tight_layout()
    path = os.path.join(save_dir, "eda_05_team_win_percentage.png")
    plt.savefig(path)
    plt.close()
    print(f"[OK] Generated {path}")


def plot_chasing_vs_defending(df_m, save_dir=REPORTS_DIR):
    """Plot match outcomes: Chasing vs Defending across seasons."""
    plt.figure(figsize=(12, 6), dpi=300)

    season_outcomes = df_m[df_m["win_type"].isin(["Chasing", "Defending"])].groupby(["season", "win_type"]).size().unstack(fill_value=0)
    season_pct = season_outcomes.div(season_outcomes.sum(axis=1), axis=0) * 100

    ax = season_pct.plot(kind="bar", stacked=True, color=["#1f77b4", "#ff7f0e"], edgecolor="black", figsize=(12, 6))
    plt.title("IPL Season-by-Season Match Winning Bias: Chasing vs Defending", pad=15)
    plt.xlabel("Season")
    plt.ylabel("Percentage of Matches Won (%)")
    plt.axhline(50, color="black", linestyle="--", linewidth=1, alpha=0.7)
    plt.legend(["Chasing (Bat 2nd)", "Defending (Bat 1st)"], loc="lower right")
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = os.path.join(save_dir, "eda_06_chasing_vs_defending.png")
    plt.savefig(path)
    plt.close()
    print(f"[OK] Generated {path}")


def plot_venue_scoring_bias(df_venue, save_dir=REPORTS_DIR):
    """Plot Top 12 Venues: 1st Innings Average Score & Chasing Win %."""
    plt.figure(figsize=(12, 6), dpi=300)
    top_venues = df_venue.head(12).sort_values(by="avg_first_innings_score", ascending=True)

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
    ax2 = ax1.twinx()

    y_pos = np.arange(len(top_venues))
    width = 0.4

    b1 = ax1.barh(y_pos - width/2, top_venues["avg_first_innings_score"], width, color="#3470a3", label="Avg 1st Innings Score", edgecolor="black")
    b2 = ax2.barh(y_pos + width/2, top_venues["chase_win_pct"], width, color="#ff9e4a", label="Chasing Win %", edgecolor="black")

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(top_venues["venue_name"])
    ax1.set_xlabel("Average 1st Innings Score", color="#3470a3", fontweight="bold")
    ax2.set_xlabel("Chasing Win %", color="#ff9e4a", fontweight="bold")
    ax1.set_xlim(120, 200)
    ax2.set_xlim(30, 75)

    plt.title("Venue Characteristics: 1st Innings Average Score vs Chasing Advantage", pad=15)
    fig.tight_layout()
    path = os.path.join(save_dir, "eda_07_venue_scoring_bias.png")
    plt.savefig(path)
    plt.close()
    print(f"[OK] Generated {path}")


def generate_all_eda_visualizations():
    """Generates all 7 portfolio visual assets."""
    print("=" * 65)
    print("PHASE 5: GENERATING EXPLORATORY DATA ANALYSIS VISUALIZATIONS")
    print("=" * 65)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    df_bat = pd.read_csv(os.path.join(PROCESSED_DIR, "agg_batting_career.csv"))
    df_bowl = pd.read_csv(os.path.join(PROCESSED_DIR, "agg_bowling_career.csv"))
    df_team = pd.read_csv(os.path.join(PROCESSED_DIR, "agg_team_overall.csv"))
    df_venue = pd.read_csv(os.path.join(PROCESSED_DIR, "agg_venue_stats.csv"))
    df_m = pd.read_csv(os.path.join(PROCESSED_DIR, "matches_clean.csv"))

    plot_top_batsmen(df_bat)
    plot_top_bowlers(df_bowl)
    plot_batting_quadrant(df_bat)
    plot_bowling_quadrant(df_bowl)
    plot_team_win_pct(df_team)
    plot_chasing_vs_defending(df_m)
    plot_venue_scoring_bias(df_venue)

    print("=" * 65)
    print(f"All EDA visualizations generated successfully in {REPORTS_DIR}!")
    print("=" * 65)


if __name__ == "__main__":
    generate_all_eda_visualizations()
