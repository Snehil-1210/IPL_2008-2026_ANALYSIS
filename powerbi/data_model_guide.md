# Power BI Data Modeling & Relationship Guide
## Cricket Analytics & Performance Intelligence System

This document outlines the step-by-step blueprint to construct the enterprise Star Schema data model in **Power BI Desktop**.

---

### 1. Data Import Instructions

1. Open **Power BI Desktop**.
2. Click **Get Data** $\rightarrow$ **Text/CSV**.
3. Navigate to your project folder: `data/processed/`.
4. Import the following tables:
   - **Dimension Tables**:
     - `dim_team.csv`
     - `dim_player.csv`
     - `dim_venue.csv`
     - `dim_date.csv`
   - **Fact Tables**:
     - `fact_matches.csv`
     - `fact_ballbyball.csv`
   - **Analytical Aggregate Tables (High-Performance Tables)**:
     - `agg_batting_career.csv`
     - `agg_bowling_career.csv`
     - `agg_team_overall.csv`
     - `agg_venue_stats.csv`

---

### 2. Star Schema Relationship Architecture (Model View)

Navigate to the **Model View** (left navigation rail). Create the following relationships (Cardinality: **1 to Many (1:\*)**, Cross filter direction: **Single**):

| Primary Key (Dimension Table) | Foreign Key (Fact Table) | Relationship State | Cardinality |
| :--- | :--- | :--- | :--- |
| `dim_date[date_key]` | `fact_matches[date_key]` | **Active** | 1 to Many ($1:*$) |
| `dim_venue[venue_key]` | `fact_matches[venue_key]` | **Active** | 1 to Many ($1:*$) |
| `dim_team[team_key]` | `fact_matches[winner_key]` | **Active** | 1 to Many ($1:*$) |
| `dim_team[team_key]` | `fact_matches[team1_key]` | Inactive | 1 to Many ($1:*$) |
| `dim_team[team_key]` | `fact_matches[team2_key]` | Inactive | 1 to Many ($1:*$) |
| `fact_matches[match_key]` | `fact_ballbyball[match_key]` | **Active** | 1 to Many ($1:*$) |
| `dim_player[player_key]` | `fact_ballbyball[striker_key]` | **Active** | 1 to Many ($1:*$) |
| `dim_player[player_key]` | `fact_ballbyball[bowler_key]` | Inactive | 1 to Many ($1:*$) |
| `dim_team[team_key]` | `fact_ballbyball[batting_team_key]` | **Active** | 1 to Many ($1:*$) |
| `dim_team[team_key]` | `fact_ballbyball[bowling_team_key]` | Inactive | 1 to Many ($1:*$) |

> **Best Practice Tip for Role-Playing Dimensions**: 
> When measuring bowling figures, use the DAX function `USERELATIONSHIP(dim_player[player_key], fact_ballbyball[bowler_key])` to activate the bowler link dynamically. Alternatively, the pre-built `agg_bowling_career` table links directly to `dim_player[player_name]` without relationship switching.

---

### 3. Fields to Hide from Report View

To keep the report canvas clean and prevent users from inadvertently slicing by unformatted surrogate keys, right-click and choose **Hide in report view** for:
- `fact_matches[date_key]`, `[venue_key]`, `[team1_key]`, `[team2_key]`, `[winner_key]`, `[toss_winner_key]`
- `fact_ballbyball[batting_team_key]`, `[bowling_team_key]`, `[striker_key]`, `[bowler_key]`, `[non_striker_key]`

---

### 4. Creating the DAX Measures Table

1. In the **Home** tab, click **Enter Data**.
2. Name the table `_Measures` and click **Load**.
3. Create new measures by copying and pasting the formulas from [`powerbi/dax_measures.txt`](file:///c:/Users/KIIT0001/OneDrive/Desktop/SPORTS/powerbi/dax_measures.txt).
4. Delete the default blank column (`Column1`) from `_Measures`. The table will automatically jump to the top of your Data Pane with a calculator icon.

---

### 5. Formatting Standards

Apply these formatting settings to the measures in Power BI:
- **Percentages** (`Win %`, `Strike Rate`, `Boundary %`, `Dot Ball %`): Format as `0.0%` or `0.00`.
- **Averages & Rates** (`Batting Average`, `Economy Rate`, `Bowling Strike Rate`): Format as Decimal Number with 2 decimal places.
- **Counts** (`Total Runs`, `Total Wickets`, `Total Matches`): Format as Whole Number with thousands separator (e.g. `1,243`).
