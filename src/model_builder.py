"""
Cricket Analytics System: Data Modeling & Star Schema Generation Module
Transforms cleaned data into Star Schema Fact and Dimension tables for Power BI.
"""

import os
import time
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# Team short codes for clean Power BI badges
TEAM_SHORT_CODES = {
    "Chennai Super Kings": "CSK",
    "Mumbai Indians": "MI",
    "Kolkata Knight Riders": "KKR",
    "Royal Challengers Bengaluru": "RCB",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Sunrisers Hyderabad": "SRH",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
    "Deccan Chargers": "DCG",
    "Gujarat Lions": "GL",
    "Rising Pune Supergiant": "RPS",
    "Pune Warriors": "PWI",
    "Kochi Tuskers Kerala": "KTK"
}

# Country mapping for venues
def get_venue_country(city, venue):
    venue_str = str(venue).lower()
    city_str = str(city).lower()
    if any(c in city_str or c in venue_str for c in ["dubai", "sharjah", "abu dhabi", "zayed"]):
        return "United Arab Emirates"
    if any(c in city_str or c in venue_str for c in ["cape town", "durban", "centurion", "johannesburg", "port elizabeth", "bloemfontein", "east london", "kimberley", "newlands", "kingsmead", "supersport park", "wanderers", "buffalo park"]):
        return "South Africa"
    return "India"


def build_star_schema(processed_dir=PROCESSED_DIR):
    """
    Constructs Star Schema:
    - Dim_Team
    - Dim_Player
    - Dim_Venue
    - Dim_Date
    - Fact_Matches
    - Fact_BallByBall
    """
    t0 = time.time()
    print("=" * 65)
    print("PHASE 3: BUILDING STAR SCHEMA DATA MODEL FOR POWER BI")
    print("=" * 65)

    matches_clean_path = os.path.join(processed_dir, "matches_clean.csv")
    deliveries_clean_path = os.path.join(processed_dir, "deliveries_clean.csv")

    df_m = pd.read_csv(matches_clean_path)
    df_d = pd.read_csv(deliveries_clean_path, low_memory=False)

    # -------------------------------------------------------------
    # 1. DIM_TEAM
    # -------------------------------------------------------------
    all_teams = sorted(list(set(df_m["team1"].dropna().unique()) | set(df_m["team2"].dropna().unique())))
    dim_team = pd.DataFrame({
        "team_key": range(1, len(all_teams) + 1),
        "team_name": all_teams,
        "team_code": [TEAM_SHORT_CODES.get(t, t[:3].upper()) for t in all_teams]
    })
    team_to_key = dict(zip(dim_team["team_name"], dim_team["team_key"]))

    # -------------------------------------------------------------
    # 2. DIM_PLAYER
    # -------------------------------------------------------------
    strikers = df_d["striker"].dropna().unique()
    non_strikers = df_d["non_striker"].dropna().unique()
    bowlers = df_d["bowler"].dropna().unique()
    moms = df_m["player_of_match"].dropna().unique()
    all_players = sorted(list(set(strikers) | set(non_strikers) | set(bowlers) | set(moms)))

    dim_player = pd.DataFrame({
        "player_key": range(1, len(all_players) + 1),
        "player_name": all_players
    })
    player_to_key = dict(zip(dim_player["player_name"], dim_player["player_key"]))

    # -------------------------------------------------------------
    # 3. DIM_VENUE
    # -------------------------------------------------------------
    venue_df = df_m[["venue", "city"]].drop_duplicates(subset=["venue"]).copy()
    venue_df.sort_values(by="venue", inplace=True)
    venue_df.reset_index(drop=True, inplace=True)
    venue_df["venue_key"] = range(1, len(venue_df) + 1)
    venue_df["country"] = venue_df.apply(lambda r: get_venue_country(r["city"], r["venue"]), axis=1)
    dim_venue = venue_df[["venue_key", "venue", "city", "country"]].rename(
        columns={"venue": "venue_name"}
    )
    venue_to_key = dict(zip(dim_venue["venue_name"], dim_venue["venue_key"]))

    # -------------------------------------------------------------
    # 4. DIM_DATE
    # -------------------------------------------------------------
    dates = pd.to_datetime(df_m["date"]).dropna().drop_duplicates().sort_values()
    dim_date = pd.DataFrame({"full_date": dates})
    dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["month_name"] = dim_date["full_date"].dt.strftime("%B")
    dim_date["day"] = dim_date["full_date"].dt.day
    dim_date["day_name"] = dim_date["full_date"].dt.strftime("%A")
    dim_date["day_of_week"] = dim_date["full_date"].dt.dayofweek + 1
    dim_date["quarter"] = "Q" + dim_date["full_date"].dt.quarter.astype(str)
    dim_date = dim_date[["date_key", "full_date", "year", "month", "month_name", "day", "day_name", "day_of_week", "quarter"]]

    # -------------------------------------------------------------
    # 5. FACT_MATCHES
    # -------------------------------------------------------------
    fact_matches = df_m.copy()
    fact_matches["match_key"] = fact_matches["match_id"]
    fact_matches["date_key"] = pd.to_datetime(fact_matches["date"]).dt.strftime("%Y%m%d").fillna(0).astype(int)
    fact_matches["venue_key"] = fact_matches["venue"].map(venue_to_key).fillna(0).astype(int)
    fact_matches["team1_key"] = fact_matches["team1"].map(team_to_key).fillna(0).astype(int)
    fact_matches["team2_key"] = fact_matches["team2"].map(team_to_key).fillna(0).astype(int)
    fact_matches["toss_winner_key"] = fact_matches["toss_winner"].map(team_to_key).fillna(0).astype(int)
    fact_matches["winner_key"] = fact_matches["winner"].map(team_to_key).fillna(0).astype(int)
    fact_matches["player_of_match_key"] = fact_matches["player_of_match"].map(player_to_key).fillna(0).astype(int)

    # Reorder Fact_Matches
    fact_matches_cols = [
        "match_key", "season", "date_key", "venue_key", "team1_key", "team2_key",
        "toss_winner_key", "toss_decision", "winner_key", "win_type",
        "margin", "margin_unit", "is_toss_win_match_win", "player_of_match_key",
        "eliminator", "method", "team1", "team2", "winner", "venue"
    ]
    fact_matches = fact_matches[fact_matches_cols]

    # -------------------------------------------------------------
    # 6. FACT_BALLBYBALL
    # -------------------------------------------------------------
    fact_deliv = df_d.copy()
    fact_deliv["match_key"] = fact_deliv["match_id"]
    fact_deliv["venue_key"] = fact_deliv["venue"].map(venue_to_key).fillna(0).astype(int)
    fact_deliv["batting_team_key"] = fact_deliv["batting_team"].map(team_to_key).fillna(0).astype(int)
    fact_deliv["bowling_team_key"] = fact_deliv["bowling_team"].map(team_to_key).fillna(0).astype(int)
    fact_deliv["striker_key"] = fact_deliv["striker"].map(player_to_key).fillna(0).astype(int)
    fact_deliv["non_striker_key"] = fact_deliv["non_striker"].map(player_to_key).fillna(0).astype(int)
    fact_deliv["bowler_key"] = fact_deliv["bowler"].map(player_to_key).fillna(0).astype(int)

    fact_deliv_cols = [
        "match_key", "season", "venue_key", "innings", "over", "ball_number",
        "match_phase", "batting_team_key", "bowling_team_key", "striker_key",
        "non_striker_key", "bowler_key", "runs_off_bat", "extras", "wides",
        "noballs", "byes", "legbyes", "penalty", "total_runs", "bowler_runs",
        "is_ball_faced", "is_legal_ball", "is_dot_ball", "is_four", "is_six",
        "is_boundary", "is_wicket", "is_bowler_wicket", "is_run_out", "wicket_type",
        "batting_team", "bowling_team", "striker", "bowler", "venue"
    ]
    fact_deliv = fact_deliv[fact_deliv_cols]

    # Save Star Schema tables
    dim_team.to_csv(os.path.join(processed_dir, "dim_team.csv"), index=False)
    dim_player.to_csv(os.path.join(processed_dir, "dim_player.csv"), index=False)
    dim_venue.to_csv(os.path.join(processed_dir, "dim_venue.csv"), index=False)
    dim_date.to_csv(os.path.join(processed_dir, "dim_date.csv"), index=False)
    fact_matches.to_csv(os.path.join(processed_dir, "fact_matches.csv"), index=False)
    fact_deliv.to_csv(os.path.join(processed_dir, "fact_ballbyball.csv"), index=False)

    print(f"[OK] Dim_Team:        {len(dim_team)} rows")
    print(f"[OK] Dim_Player:      {len(dim_player)} rows")
    print(f"[OK] Dim_Venue:       {len(dim_venue)} rows")
    print(f"[OK] Dim_Date:        {len(dim_date)} rows")
    print(f"[OK] Fact_Matches:    {len(fact_matches)} rows")
    print(f"[OK] Fact_BallByBall: {len(fact_deliv)} rows")
    print(f"Star Schema successfully built in {time.time() - t0:.2f}s!")


if __name__ == "__main__":
    build_star_schema()
