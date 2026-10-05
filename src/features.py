"""
Cricket Analytics System: Feature Engineering Module
Computes batting, bowling, team, venue, and advanced performance intelligence metrics.
"""

import os
import time
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def compute_batting_features(df_d, df_m):
    """
    Computes batting metrics at career and season levels.
    """
    print("Computing batting features (Career & Season)...")
    m_col = "match_id" if "match_id" in df_d.columns else "match_key"

    def build_batting_agg(group_cols):
        # 1. Base aggregations
        agg_dict = {
            "runs_off_bat": "sum",
            "is_ball_faced": "sum",
            "is_four": "sum",
            "is_six": "sum",
            "is_dot_ball": "sum",
            m_col: "nunique"
        }
        res = df_d.groupby(group_cols).agg(agg_dict).reset_index()
        res.rename(columns={
            "runs_off_bat": "runs",
            "is_ball_faced": "balls_faced",
            "is_four": "fours",
            "is_six": "sixes",
            "is_dot_ball": "dot_balls",
            m_col: "matches"
        }, inplace=True)

        # Innings count: unique match_id + innings pairs per player/season
        inns = df_d[group_cols + [m_col, "innings"]].drop_duplicates().groupby(group_cols).size().reset_index(name="innings")
        res = res.merge(inns, on=group_cols, how="left")

        # 2. Phase breakdowns
        pp = df_d[df_d["match_phase"] == "Powerplay"].groupby(group_cols).agg(
            pp_runs=("runs_off_bat", "sum"),
            pp_balls=("is_ball_faced", "sum")
        ).reset_index()
        res = res.merge(pp, on=group_cols, how="left")
        res["pp_runs"] = res["pp_runs"].fillna(0).astype(int)
        res["pp_balls"] = res["pp_balls"].fillna(0).astype(int)

        mid = df_d[df_d["match_phase"] == "Middle"].groupby(group_cols).agg(
            mid_runs=("runs_off_bat", "sum")
        ).reset_index()
        res = res.merge(mid, on=group_cols, how="left")
        res["mid_runs"] = res["mid_runs"].fillna(0).astype(int)

        death = df_d[df_d["match_phase"] == "Death"].groupby(group_cols).agg(
            death_runs=("runs_off_bat", "sum"),
            death_balls=("is_ball_faced", "sum")
        ).reset_index()
        res = res.merge(death, on=group_cols, how="left")
        res["death_runs"] = res["death_runs"].fillna(0).astype(int)
        res["death_balls"] = res["death_balls"].fillna(0).astype(int)

        # 3. Dismissals count
        dismissed_mask = (df_d["player_dismissed"].notna()) & (df_d["player_dismissed"] == df_d["striker"])
        d_sub = df_d[dismissed_mask].groupby(group_cols).size().reset_index(name="dismissals")
        res = res.merge(d_sub, on=group_cols, how="left")
        res["dismissals"] = res["dismissals"].fillna(0).astype(int)

        # 4. Rates & Metrics
        res["batting_average"] = np.where(
            res["dismissals"] == 0,
            res["runs"].astype(float),
            (res["runs"] / res["dismissals"])
        ).round(2)

        res["strike_rate"] = np.where(
            res["balls_faced"] == 0,
            0.0,
            (res["runs"] / res["balls_faced"] * 100.0)
        ).round(2)

        res["boundary_runs"] = (res["fours"] * 4) + (res["sixes"] * 6)
        res["boundary_pct"] = np.where(
            res["runs"] == 0,
            0.0,
            (res["boundary_runs"] / res["runs"] * 100.0)
        ).round(2)

        res["runs_per_inning"] = np.where(
            res["innings"] == 0,
            0.0,
            (res["runs"] / res["innings"])
        ).round(2)

        res["pp_strike_rate"] = np.where(
            res["pp_balls"] == 0,
            0.0,
            (res["pp_runs"] / res["pp_balls"] * 100.0)
        ).round(2)

        res["death_strike_rate"] = np.where(
            res["death_balls"] == 0,
            0.0,
            (res["death_runs"] / res["death_balls"] * 100.0)
        ).round(2)

        # 5. Advanced Batting Impact Index:
        # Volume weighting + scoring acceleration relative to 130 T20 par + boundary reliance
        res["batting_impact"] = (
            (res["runs_per_inning"] * 0.4) +
            ((res["strike_rate"] / 100.0) * 20.0) +
            (res["boundary_pct"] * 0.5)
        ).round(2)

        return res

    batting_career = build_batting_agg(["striker"])
    batting_career.rename(columns={"striker": "player_name"}, inplace=True)
    batting_career.sort_values(by="runs", ascending=False, inplace=True)

    batting_season = build_batting_agg(["striker", "season"])
    batting_season.rename(columns={"striker": "player_name"}, inplace=True)
    batting_season.sort_values(by=["season", "runs"], ascending=[True, False], inplace=True)

    return batting_career, batting_season


def compute_bowling_features(df_d, df_m):
    """
    Computes bowling metrics at career and season levels.
    """
    print("Computing bowling features (Career & Season)...")
    m_col = "match_id" if "match_id" in df_d.columns else "match_key"

    def build_bowling_agg(group_cols):
        agg_dict = {
            "is_bowler_wicket": "sum",
            "bowler_runs": "sum",
            "is_legal_ball": "sum",
            "is_dot_ball": "sum",
            m_col: "nunique"
        }
        res = df_d.groupby(group_cols).agg(agg_dict).reset_index()
        res.rename(columns={
            "is_bowler_wicket": "wickets",
            "bowler_runs": "runs_conceded",
            "is_legal_ball": "legal_balls",
            "is_dot_ball": "dot_balls",
            m_col: "matches"
        }, inplace=True)

        inns = df_d[group_cols + [m_col, "innings"]].drop_duplicates().groupby(group_cols).size().reset_index(name="innings")
        res = res.merge(inns, on=group_cols, how="left")

        # Phase breakdowns
        pp = df_d[df_d["match_phase"] == "Powerplay"].groupby(group_cols).agg(
            pp_wickets=("is_bowler_wicket", "sum"),
            pp_balls=("is_legal_ball", "sum"),
            pp_runs=("bowler_runs", "sum")
        ).reset_index()
        res = res.merge(pp, on=group_cols, how="left")
        res["pp_wickets"] = res["pp_wickets"].fillna(0).astype(int)
        res["pp_balls"] = res["pp_balls"].fillna(0).astype(int)
        res["pp_runs"] = res["pp_runs"].fillna(0).astype(int)

        death = df_d[df_d["match_phase"] == "Death"].groupby(group_cols).agg(
            death_wickets=("is_bowler_wicket", "sum"),
            death_balls=("is_legal_ball", "sum"),
            death_runs=("bowler_runs", "sum")
        ).reset_index()
        res = res.merge(death, on=group_cols, how="left")
        res["death_wickets"] = res["death_wickets"].fillna(0).astype(int)
        res["death_balls"] = res["death_balls"].fillna(0).astype(int)
        res["death_runs"] = res["death_runs"].fillna(0).astype(int)

        # Overs display and exact calculation
        res["overs"] = (res["legal_balls"] // 6) + ((res["legal_balls"] % 6) / 10.0)
        res["exact_overs"] = res["legal_balls"] / 6.0

        # Derived Rates
        res["economy_rate"] = np.where(
            res["exact_overs"] == 0,
            0.0,
            (res["runs_conceded"] / res["exact_overs"])
        ).round(2)

        res["bowling_average"] = np.where(
            res["wickets"] == 0,
            np.nan,
            (res["runs_conceded"] / res["wickets"])
        ).round(2)

        res["bowling_strike_rate"] = np.where(
            res["wickets"] == 0,
            np.nan,
            (res["legal_balls"] / res["wickets"])
        ).round(2)

        res["dot_ball_pct"] = np.where(
            res["legal_balls"] == 0,
            0.0,
            (res["dot_balls"] / res["legal_balls"] * 100.0)
        ).round(2)

        res["pp_economy"] = np.where(
            res["pp_balls"] == 0,
            0.0,
            (res["pp_runs"] / (res["pp_balls"] / 6.0))
        ).round(2)

        res["death_economy"] = np.where(
            res["death_balls"] == 0,
            0.0,
            (res["death_runs"] / (res["death_balls"] / 6.0))
        ).round(2)

        # Advanced Bowling Impact Index:
        # Wicket-taking frequency per innings + economy suppression vs 8.5 par + dot ball pressure
        res["wickets_per_inning"] = np.where(res["innings"] == 0, 0.0, (res["wickets"] / res["innings"])).round(2)
        economy_suppression = np.maximum(0, 8.5 - res["economy_rate"])
        res["bowling_impact"] = (
            (res["wickets_per_inning"] * 25.0) +
            (economy_suppression * 8.0) +
            (res["dot_ball_pct"] * 0.4)
        ).round(2)

        return res

    bowling_career = build_bowling_agg(["bowler"])
    bowling_career.rename(columns={"bowler": "player_name"}, inplace=True)
    bowling_career.sort_values(by="wickets", ascending=False, inplace=True)

    bowling_season = build_bowling_agg(["bowler", "season"])
    bowling_season.rename(columns={"bowler": "player_name"}, inplace=True)
    bowling_season.sort_values(by=["season", "wickets"], ascending=[True, False], inplace=True)

    return bowling_career, bowling_season


def compute_team_features(df_m, df_d):
    """
    Computes team performance metrics overall and season-by-season.
    """
    print("Computing team analytics (Overall & Season)...")
    m_col = "match_id" if "match_id" in df_d.columns else "match_key"

    def build_team_agg(group_by_season=False):
        records = []
        seasons = sorted(df_m["season"].unique()) if group_by_season else [None]

        for s in seasons:
            m_sub = df_m if s is None else df_m[df_m["season"] == s]
            teams = sorted(list(set(m_sub["team1"].unique()) | set(m_sub["team2"].unique())))

            for t in teams:
                played = m_sub[(m_sub["team1"] == t) | (m_sub["team2"] == t)]
                n_matches = len(played)
                if n_matches == 0:
                    continue

                wins = len(played[played["winner"] == t])
                losses = len(played[(played["winner"].notna()) & (played["winner"] != t) & (played["winner"] != "No Result")])
                no_results = n_matches - wins - losses
                win_pct = round((wins / n_matches * 100), 2)

                # Chasing: when team bowled 1st
                chasing_matches = played[
                    ((played["toss_winner"] == t) & (played["toss_decision"] == "Field")) |
                    ((played["toss_winner"] != t) & (played["toss_decision"] == "Bat"))
                ]
                chase_wins = len(chasing_matches[chasing_matches["winner"] == t])
                chase_win_pct = round((chase_wins / len(chasing_matches) * 100), 2) if len(chasing_matches) > 0 else 0.0

                # Defending: when team batted 1st
                defending_matches = played[
                    ((played["toss_winner"] == t) & (played["toss_decision"] == "Bat")) |
                    ((played["toss_winner"] != t) & (played["toss_decision"] == "Field"))
                ]
                defend_wins = len(defending_matches[defending_matches["winner"] == t])
                defend_win_pct = round((defend_wins / len(defending_matches) * 100), 2) if len(defending_matches) > 0 else 0.0

                # Toss metrics
                toss_wins = len(played[played["toss_winner"] == t])
                toss_win_pct = round((toss_wins / n_matches * 100), 2)
                toss_and_match_wins = len(played[(played["toss_winner"] == t) & (played["winner"] == t)])
                toss_conversion_pct = round((toss_and_match_wins / toss_wins * 100), 2) if toss_wins > 0 else 0.0

                # Average team score
                t_deliv = df_d if s is None else df_d[df_d["season"] == s]
                team_innings = t_deliv[t_deliv["batting_team"] == t].groupby([m_col, "innings"])["total_runs"].sum()
                avg_score = round(team_innings.mean(), 2) if len(team_innings) > 0 else 0.0
                max_score = int(team_innings.max()) if len(team_innings) > 0 else 0

                rec = {
                    "team_name": t,
                    "matches_played": n_matches,
                    "wins": wins,
                    "losses": losses,
                    "no_results": no_results,
                    "win_pct": win_pct,
                    "chasing_matches": len(chasing_matches),
                    "chase_wins": chase_wins,
                    "chase_win_pct": chase_win_pct,
                    "defending_matches": len(defending_matches),
                    "defend_wins": defend_wins,
                    "defend_win_pct": defend_win_pct,
                    "toss_wins": toss_wins,
                    "toss_win_pct": toss_win_pct,
                    "toss_conversion_pct": toss_conversion_pct,
                    "avg_innings_score": avg_score,
                    "max_innings_score": max_score
                }
                if s is not None:
                    rec["season"] = s
                records.append(rec)

        res_df = pd.DataFrame(records)
        return res_df

    team_overall = build_team_agg(group_by_season=False)
    team_overall.sort_values(by="win_pct", ascending=False, inplace=True)

    team_season = build_team_agg(group_by_season=True)
    team_season.sort_values(by=["season", "win_pct"], ascending=[True, False], inplace=True)

    return team_overall, team_season


def compute_venue_features(df_m, df_d):
    """
    Computes venue characteristics, average 1st and 2nd innings scores, chasing advantage.
    """
    print("Computing venue analytics...")
    m_col = "match_id" if "match_id" in df_d.columns else "match_key"
    venue_stats = []
    venues = sorted(df_m["venue"].unique())

    for v in venues:
        m_v = df_m[df_m["venue"] == v]
        n_matches = len(m_v)
        if n_matches < 3:
            continue

        d_v = df_d[df_d["venue"] == v]
        inn1_scores = d_v[d_v["innings"] == 1].groupby(m_col)["total_runs"].sum()
        inn2_scores = d_v[d_v["innings"] == 2].groupby(m_col)["total_runs"].sum()

        avg_inn1 = round(inn1_scores.mean(), 1) if len(inn1_scores) > 0 else 0.0
        avg_inn2 = round(inn2_scores.mean(), 1) if len(inn2_scores) > 0 else 0.0

        chase_wins = len(m_v[m_v["win_type"] == "Chasing"])
        defend_wins = len(m_v[m_v["win_type"] == "Defending"])
        super_overs = len(m_v[m_v["win_type"] == "Super Over"])

        chase_win_pct = round((chase_wins / n_matches * 100), 1)
        toss_match_wins = len(m_v[m_v["is_toss_win_match_win"] == 1])
        toss_impact_pct = round((toss_match_wins / n_matches * 100), 1)

        venue_stats.append({
            "venue_name": v,
            "matches_hosted": n_matches,
            "avg_first_innings_score": avg_inn1,
            "avg_second_innings_score": avg_inn2,
            "chasing_wins": chase_wins,
            "defending_wins": defend_wins,
            "super_overs": super_overs,
            "chase_win_pct": chase_win_pct,
            "toss_match_win_pct": toss_impact_pct
        })

    df_venue = pd.DataFrame(venue_stats)
    df_venue.sort_values(by="matches_hosted", ascending=False, inplace=True)
    return df_venue


def run_feature_engineering_pipeline():
    """Executes full feature engineering and exports analytics datasets."""
    t0 = time.time()
    print("=" * 65)
    print("PHASE 4 & 6: ADVANCED CRICKET FEATURE ENGINEERING")
    print("=" * 65)

    df_m = pd.read_csv(os.path.join(PROCESSED_DIR, "matches_clean.csv"))
    df_d = pd.read_csv(os.path.join(PROCESSED_DIR, "deliveries_clean.csv"), low_memory=False)

    bat_career, bat_season = compute_batting_features(df_d, df_m)
    bowl_career, bowl_season = compute_bowling_features(df_d, df_m)
    team_overall, team_season = compute_team_features(df_m, df_d)
    venue_stats = compute_venue_features(df_m, df_d)

    # Save to data/processed
    bat_career.to_csv(os.path.join(PROCESSED_DIR, "agg_batting_career.csv"), index=False)
    bat_season.to_csv(os.path.join(PROCESSED_DIR, "agg_batting_season.csv"), index=False)
    bowl_career.to_csv(os.path.join(PROCESSED_DIR, "agg_bowling_career.csv"), index=False)
    bowl_season.to_csv(os.path.join(PROCESSED_DIR, "agg_bowling_season.csv"), index=False)
    team_overall.to_csv(os.path.join(PROCESSED_DIR, "agg_team_overall.csv"), index=False)
    team_season.to_csv(os.path.join(PROCESSED_DIR, "agg_team_season.csv"), index=False)
    venue_stats.to_csv(os.path.join(PROCESSED_DIR, "agg_venue_stats.csv"), index=False)

    print("\n" + "=" * 65)
    print("FEATURE ENGINEERING SUMMARY & VALIDATION:")
    print("=" * 65)
    print(f"Batting Career Records: {len(bat_career):,} players")
    print(f"Batting Season Records: {len(bat_season):,} player-seasons")
    print(f"Bowling Career Records: {len(bowl_career):,} bowlers")
    print(f"Bowling Season Records: {len(bowl_season):,} bowler-seasons")
    print(f"Team Overall Records:   {len(team_overall):,} franchises")
    print(f"Team Season Records:    {len(team_season):,} team-seasons")
    print(f"Major Venues Analyzed:  {len(venue_stats):,} grounds")
    print(f"Top Run Scorer:         {bat_career.iloc[0]['player_name']} ({bat_career.iloc[0]['runs']:,} runs, Impact: {bat_career.iloc[0]['batting_impact']})")
    print(f"Top Wicket Taker:       {bowl_career.iloc[0]['player_name']} ({bowl_career.iloc[0]['wickets']:,} wickets, Impact: {bowl_career.iloc[0]['bowling_impact']})")
    print(f"Pipeline executed in {time.time() - t0:.2f}s!")
    print("=" * 65)


if __name__ == "__main__":
    run_feature_engineering_pipeline()
