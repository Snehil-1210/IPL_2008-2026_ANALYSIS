"""
Cricket Analytics System: Data Acquisition Module
Source: Cricsheet (Official IPL Ball-by-Ball and Match Registry, 2008-2024)
"""

import os
import time
import zipfile
import urllib.request
import shutil
import pandas as pd

CRICSHEET_IPL_URL = "https://cricsheet.org/downloads/ipl_csv2.zip"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")


def download_and_extract_ipl_data(raw_dir=RAW_DATA_DIR):
    """
    Downloads the official Cricsheet IPL dataset, parses match info files into
    `matches_raw.csv` and extracts ball-by-ball deliveries into `deliveries_raw.csv`.
    """
    os.makedirs(raw_dir, exist_ok=True)
    zip_path = os.path.join(raw_dir, "temp_ipl.zip")
    matches_csv_path = os.path.join(raw_dir, "matches_raw.csv")
    deliveries_csv_path = os.path.join(raw_dir, "deliveries_raw.csv")

    print("=" * 65)
    print("PHASE 1: ACQUIRING OFFICIAL IPL DATASET (2008 - 2024)")
    print("=" * 65)
    print(f"Connecting to: {CRICSHEET_IPL_URL}...")
    t0 = time.time()

    req = urllib.request.Request(CRICSHEET_IPL_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=45) as resp, open(zip_path, "wb") as out_f:
        total_size = int(resp.headers.get("content-length", 0))
        downloaded = 0
        chunk_size = 128 * 1024
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out_f.write(chunk)
            downloaded += len(chunk)

    print(f"[OK] Download completed ({os.path.getsize(zip_path) / 1024 / 1024:.2f} MB) in {time.time() - t0:.2f}s.")

    with zipfile.ZipFile(zip_path, "r") as zf:
        print("Extracting ball-by-ball deliveries (all_matches.csv)...", flush=True)
        # Extract all_matches.csv
        zf.extract("all_matches.csv", path=raw_dir)
        extracted_file = os.path.join(raw_dir, "all_matches.csv")
        if os.path.exists(deliveries_csv_path):
            os.remove(deliveries_csv_path)
        os.rename(extracted_file, deliveries_csv_path)
        print(f"[OK] Saved ball-by-ball dataset -> {deliveries_csv_path}", flush=True)

        # Parse match metadata from *_info.csv files
        print("Parsing match-level information files...", flush=True)
        info_files = [f for f in zf.namelist() if f.endswith("_info.csv")]
        print(f"Found {len(info_files)} match metadata files. Parsing records...", flush=True)

        matches_list = []
        for fname in info_files:
            content = zf.read(fname).decode("utf-8")
            lines = content.strip().split("\n")
            m_info = {}
            teams = []
            for line in lines:
                parts = [p.strip().strip('"') for p in line.split(",")]
                if len(parts) >= 3 and parts[0] == "info":
                    key = parts[1]
                    val = parts[2]
                    if key == "team":
                        teams.append(val)
                    elif key in [
                        "match_id",
                        "season",
                        "date",
                        "venue",
                        "city",
                        "toss_winner",
                        "toss_decision",
                        "player_of_match",
                        "winner",
                        "winner_runs",
                        "winner_wickets",
                        "result",
                        "eliminator",
                        "method",
                    ]:
                        m_info[key] = val
            if len(teams) >= 2:
                m_info["team1"] = teams[0]
                m_info["team2"] = teams[1]
            matches_list.append(m_info)

        df_matches = pd.DataFrame(matches_list)
        df_matches.sort_values(by=["date", "match_id"], inplace=True)
        df_matches.to_csv(matches_csv_path, index=False)
        print(f"[OK] Saved matches dataset -> {matches_csv_path}", flush=True)

    # Clean up temp zip
    if os.path.exists(zip_path):
        os.remove(zip_path)

    # Summary validation
    df_deliv = pd.read_csv(deliveries_csv_path, nrows=5)
    total_deliveries = sum(1 for _ in open(deliveries_csv_path, "r", encoding="utf-8")) - 1
    print("\n" + "=" * 65)
    print("DATA ACQUISITION SUMMARY & VALIDATION:")
    print("=" * 65)
    print(f"Total Matches:      {len(df_matches):,}")
    print(f"Total Deliveries:   {total_deliveries:,}")
    print(f"Seasons covered:    {df_matches['season'].min()} to {df_matches['season'].max()}")
    print(f"Matches Columns:    {list(df_matches.columns)}")
    print(f"Deliveries Columns: {list(df_deliv.columns)}")
    print("=" * 65)
    print("Phase 1 verification successful! Ready for Phase 2 (Data Cleaning).")


if __name__ == "__main__":
    download_and_extract_ipl_data()
