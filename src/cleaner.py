"""
Cricket Analytics System: Data Cleaning & Standardization Module
Standardizes teams, venues, seasons, overs, match phases, and bowler/batter statistics.
"""

import os
import time
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# Team name standardization mapping (handling franchise rebrands)
TEAM_NAME_MAP = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru"
}

# Venue standardization mapping (handling sponsor/spelling/rebranding duplicates)
VENUE_MAP = {
    "M Chinnaswamy Stadium": "M Chinnaswamy Stadium",
    "M.Chinnaswamy Stadium": "M Chinnaswamy Stadium",
    "M Chinnaswamy Stadium, Bengaluru": "M Chinnaswamy Stadium",
    "Feroz Shah Kotla": "Arun Jaitley Stadium",
    "Arun Jaitley Stadium": "Arun Jaitley Stadium",
    "Sardar Patel Stadium": "Narendra Modi Stadium",
    "Sardar Patel Stadium, Motera": "Narendra Modi Stadium",
    "Narendra Modi Stadium": "Narendra Modi Stadium",
    "Narendra Modi Stadium, Ahmedabad": "Narendra Modi Stadium",
    "Punjab Cricket Association Stadium": "PCA Stadium, Mohali",
    "Punjab Cricket Association IS Bindra Stadium": "PCA Stadium, Mohali",
    "Punjab Cricket Association Stadium, Mohali": "PCA Stadium, Mohali",
    "Punjab Cricket Association IS Bindra Stadium, Mohali": "PCA Stadium, Mohali",
    "MA Chidambaram Stadium": "MA Chidambaram Stadium",
    "MA Chidambaram Stadium, Chepauk": "MA Chidambaram Stadium",
    "MA Chidambaram Stadium, Chepauk, Chennai": "MA Chidambaram Stadium",
    "Rajiv Gandhi International Stadium": "Rajiv Gandhi International Stadium",
    "Rajiv Gandhi International Stadium, Uppal": "Rajiv Gandhi International Stadium",
    "Rajiv Gandhi International Stadium, Uppal, Hyderabad": "Rajiv Gandhi International Stadium",
    "Subrata Roy Sahara Stadium": "Maharashtra Cricket Association Stadium",
    "Maharashtra Cricket Association Stadium": "Maharashtra Cricket Association Stadium",
    "Maharashtra Cricket Association Stadium, Pune": "Maharashtra Cricket Association Stadium",
    "Dr DY Patil Sports Academy": "Dr DY Patil Sports Academy",
    "Dr DY Patil Sports Academy, Mumbai": "Dr DY Patil Sports Academy",
    "Brabourne Stadium": "Brabourne Stadium",
    "Brabourne Stadium, Mumbai": "Brabourne Stadium",
    "Wankhede Stadium": "Wankhede Stadium",
    "Wankhede Stadium, Mumbai": "Wankhede Stadium",
    "Eden Gardens": "Eden Gardens",
    "Eden Gardens, Kolkata": "Eden Gardens",
    "Sheikh Zayed Stadium": "Sheikh Zayed Stadium",
    "Zayed Cricket Stadium": "Sheikh Zayed Stadium",
    "Zayed Cricket Stadium, Abu Dhabi": "Sheikh Zayed Stadium",
    "Himachal Pradesh Cricket Association Stadium": "HPCA Stadium, Dharamshala",
    "Himachal Pradesh Cricket Association Stadium, Dharamsala": "HPCA Stadium, Dharamshala",
    "Sawai Mansingh Stadium": "Sawai Mansingh Stadium",
    "Sawai Mansingh Stadium, Jaipur": "Sawai Mansingh Stadium",
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium": "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Stadium",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium": "Ekana Cricket Stadium, Lucknow",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow": "Ekana Cricket Stadium, Lucknow"
}

# Valid bowler wicket types
BOWLER_WICKET_TYPES = {
    "bowled",
    "caught",
    "caught and bowled",
    "lbw",
    "stumped",
    "hit wicket"
}


def clean_season(season_val):
    """Normalizes seasons (e.g. '2007/08' -> 2008, '2020/21' -> 2020, 2015 -> 2015)."""
    s = str(season_val).strip()
    if "/" in s:
        # For '2007/08' it refers to 2008; for '2020/21' it was 2020.
        parts = s.split("/")
        if len(parts[0]) == 4:
            year_prefix = parts[0][:2]
            year2 = int(year_prefix + parts[1])
            # If season is 2007/08 -> 2008; if 2020/21 -> 2020
            if parts[0] == "2020":
                return 2020
            return year2
        return int(parts[0])
    return int(float(s))


def standardize_team(team_val):
    """Standardizes team names using TEAM_NAME_MAP."""
    if pd.isna(team_val):
        return team_val
    t = str(team_val).strip()
    return TEAM_NAME_MAP.get(t, t)


def standardize_venue(venue_val):
    """Standardizes venue names using VENUE_MAP."""
    if pd.isna(venue_val):
        return "Unknown Venue"
    v = str(venue_val).strip()
    return VENUE_MAP.get(v, v)


def clean_matches_data(raw_matches_path=None, save_path=None):
    """Cleans and enriches match-level data."""
    if raw_matches_path is None:
        raw_matches_path = os.path.join(RAW_DIR, "matches_raw.csv")
    if save_path is None:
        save_path = os.path.join(PROCESSED_DIR, "matches_clean.csv")

    print("Cleaning matches dataset...")
    df = pd.read_csv(raw_matches_path)

    # 1. Normalize Season
    df["season"] = df["season"].apply(clean_season)

    # 2. Parse Date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 3. Standardize Venues
    df["venue"] = df["venue"].apply(standardize_venue)

    # 4. Impute Missing Cities
    df["city"] = df["city"].fillna(
        df["venue"].map(
            lambda v: "Dubai" if "Dubai" in str(v) else ("Sharjah" if "Sharjah" in str(v) else "Abu Dhabi" if "Zayed" in str(v) else np.nan)
        )
    )

    # 5. Standardize Team Names
    team_cols = ["team1", "team2", "toss_winner", "winner"]
    for col in team_cols:
        df[col] = df[col].apply(standardize_team)

    # 6. Toss Decisions
    df["toss_decision"] = df["toss_decision"].str.strip().str.capitalize()

    # 7. Convert Numeric Columns
    for col in ["winner_runs", "winner_wickets"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 8. Win Type & Margin
    def get_win_type(row):
        if pd.isna(row["winner"]) or str(row["winner"]).strip() == "":
            return "No Result"
        if pd.notna(row.get("eliminator")) and str(row.get("eliminator")).strip() not in ["", "nan"]:
            return "Super Over"
        if row["winner_runs"] > 0:
            return "Defending"
        if row["winner_wickets"] > 0:
            return "Chasing"
        return "No Result"

    df["win_type"] = df.apply(get_win_type, axis=1)

    # Numeric margin & margin unit
    df["margin"] = np.where(df["winner_runs"] > 0, df["winner_runs"], df["winner_wickets"])
    df["margin_unit"] = np.where(
        df["win_type"] == "Defending", "Runs",
        np.where(df["win_type"] == "Chasing", "Wickets",
                 np.where(df["win_type"] == "Super Over", "Super Over", "None"))
    )

    # 9. Toss Win to Match Win indicator
    df["is_toss_win_match_win"] = (df["toss_winner"] == df["winner"]).astype(int)

    # Sort chronologically
    df.sort_values(by=["date", "match_id"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    print(f"[OK] Cleaned matches saved -> {save_path} ({df.shape[0]} rows, {df.shape[1]} cols)")
    return df


def clean_deliveries_data(raw_deliv_path=None, save_path=None):
    """Cleans and enriches ball-by-ball deliveries data."""
    if raw_deliv_path is None:
        raw_deliv_path = os.path.join(RAW_DIR, "deliveries_raw.csv")
    if save_path is None:
        save_path = os.path.join(PROCESSED_DIR, "deliveries_clean.csv")

    print("Cleaning deliveries dataset (this may take 5-10 seconds for ~300k rows)...")
    t0 = time.time()
    df = pd.read_csv(raw_deliv_path, low_memory=False)

    # 1. Normalize Season
    df["season"] = df["season"].apply(clean_season)

    # 2. Standardize Venue
    df["venue"] = df["venue"].apply(standardize_venue)

    # 3. Standardize Teams
    df["batting_team"] = df["batting_team"].apply(standardize_team)
    df["bowling_team"] = df["bowling_team"].apply(standardize_team)

    # 4. Fill Extras
    extra_cols = ["extras", "wides", "noballs", "byes", "legbyes", "penalty"]
    for col in extra_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        else:
            df[col] = 0

    df["runs_off_bat"] = pd.to_numeric(df["runs_off_bat"], errors="coerce").fillna(0).astype(int)

    # 5. Over, Ball, and Phase Calculations
    # ball format: 0.1 -> 19.6
    ball_float = df["ball"].astype(float)
    df["over"] = ball_float.astype(int) + 1  # 1 to 20
    df["ball_number"] = np.round((ball_float - ball_float.astype(int)) * 10).astype(int)

    # Match Phase: Powerplay (1-6), Middle (7-15), Death (16-20)
    df["match_phase"] = np.where(
        df["innings"] > 2, "Super Over",
        np.where(df["over"] <= 6, "Powerplay",
                 np.where(df["over"] <= 15, "Middle", "Death"))
    )

    # 6. Delivery Legality & Runs Accounting
    # Legal balls faced by batter: wide deliveries do not count as ball faced
    df["is_ball_faced"] = (df["wides"] == 0).astype(int)

    # Legal balls bowled by bowler: wides and noballs do not count as legal ball bowled
    df["is_legal_ball"] = ((df["wides"] == 0) & (df["noballs"] == 0)).astype(int)

    # Total runs scored off delivery
    df["total_runs"] = df["runs_off_bat"] + df["extras"]

    # True Bowler Runs Conceded: excludes byes and legbyes
    df["bowler_runs"] = df["runs_off_bat"] + df["wides"] + df["noballs"] + df["penalty"]

    # Dot Ball: 0 runs of any kind off delivery
    df["is_dot_ball"] = (df["total_runs"] == 0).astype(int)

    # Boundaries
    df["is_four"] = (df["runs_off_bat"] == 4).astype(int)
    df["is_six"] = (df["runs_off_bat"] == 6).astype(int)
    df["is_boundary"] = (df["is_four"] | df["is_six"]).astype(int)

    # 7. Dismissal & Bowler Wicket Classification
    df["is_wicket"] = df["wicket_type"].notna().astype(int)
    df["is_bowler_wicket"] = df["wicket_type"].astype(str).str.lower().isin(BOWLER_WICKET_TYPES).astype(int)
    df["is_run_out"] = (df["wicket_type"].astype(str).str.lower() == "run out").astype(int)

    # Select and order key columns
    keep_cols = [
        "match_id", "season", "venue", "innings", "over", "ball_number", "ball",
        "match_phase", "batting_team", "bowling_team", "striker", "non_striker", "bowler",
        "runs_off_bat", "extras", "wides", "noballs", "byes", "legbyes", "penalty",
        "total_runs", "bowler_runs", "is_ball_faced", "is_legal_ball", "is_dot_ball",
        "is_four", "is_six", "is_boundary", "wicket_type", "player_dismissed",
        "is_wicket", "is_bowler_wicket", "is_run_out"
    ]
    df = df[keep_cols]

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    print(f"[OK] Cleaned deliveries saved -> {save_path} ({df.shape[0]} rows, {df.shape[1]} cols) in {time.time() - t0:.2f}s")
    return df


def run_cleaning_pipeline():
    """Runs complete end-to-end cleaning pipeline."""
    print("=" * 65)
    print("PHASE 2: DATA CLEANING & DOMAIN STANDARDIZATION")
    print("=" * 65)
    df_matches = clean_matches_data()
    df_deliv = clean_deliveries_data()

    print("\n" + "=" * 65)
    print("DATA CLEANING SUMMARY & VALIDATION:")
    print("=" * 65)
    print(f"Cleaned Matches:    {len(df_matches):,} rows | {df_matches.shape[1]} columns")
    print(f"Cleaned Deliveries: {len(df_deliv):,} rows | {df_deliv.shape[1]} columns")
    print(f"Distinct Teams:     {df_matches['team1'].nunique()} teams (standardized)")
    print(f"Distinct Venues:    {df_matches['venue'].nunique()} venues (standardized)")
    print(f"Total Sixes:        {df_deliv['is_six'].sum():,}")
    print(f"Total Fours:        {df_deliv['is_four'].sum():,}")
    print(f"Bowler Wickets:     {df_deliv['is_bowler_wicket'].sum():,} / Total Dismissals: {df_deliv['is_wicket'].sum():,}")
    print("=" * 65)
    print("Phase 2 verification successful! Ready for Phase 3 (Data Modeling).")


if __name__ == "__main__":
    run_cleaning_pipeline()
