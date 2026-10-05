# Power BI Multi-Page Dashboard Design Blueprint
## Cricket Analytics & Performance Intelligence

This document provides visual-by-visual layout specifications, visual types, fields, slicers, and palette definitions for building the 6-page interactive report in Power BI.

---

### Design System & Theme Settings

- **Canvas Size**: 16:9 widescreen ($1920 \times 1080$ px or $1280 \times 720$ px)
- **Palette**:
  - Primary Dark Navy (Headers/Sidebar): `#0f172a`
  - Slate Background: `#f8fafc`
  - Card/Container Background: `#ffffff`
  - Accent Electric Blue (Highlights): `#2563eb`
  - Accent Amber (Boundaries/Toss): `#f59e0b`
  - Performance Green (Wins/Wickets): `#10b981`
  - Contrast Red (Dismissals/Losses): `#ef4444`
- **Typography**: Segoe UI (Titles: 16pt Bold, Data Values: 22pt Bold, Labels: 10pt Regular).

---

### Page 1 — Executive Tournament Overview

**Goal**: High-level executive summary of the IPL ecosystem across all seasons.

#### Top KPI Cards Row
1. **Total Matches**: Card | Measure: `[Total Matches]` | Value: 1,243
2. **Total Runs**: Card | Measure: `[Total Runs]` | Value: 370k+
3. **Total Wickets**: Card | Measure: `[Total Wickets]` | Value: 13,482
4. **Total Sixes**: Card | Measure: `[Total Sixes]` | Value: 15,779
5. **Avg 1st Innings Score**: Card | Measure: `[Average 1st Innings Score]` | Value: ~165
6. **Chasing Win %**: Card | Measure: `[Chasing Win %]` | Value: 53.4%

#### Visual 1 (Left): Franchise All-Time Win Percentage
- **Visual Type**: Clustered Bar Chart
- **Y-Axis**: `Dim_Team[team_name]` (Sorted descending by Win %)
- **X-Axis**: `[Team Win %]`
- **Data Labels**: Enabled (Formatted as `0.0%`)
- **Tooltip**: `[Team Matches Played]`, `[Team Wins]`

#### Visual 2 (Center): Season-by-Season Scoring & Wickets Trend
- **Visual Type**: Line & Clustered Column Chart
- **Shared X-Axis**: `Dim_Date[Year]`
- **Column Values**: `[Total Runs]`
- **Line Values**: `[Total Wickets]`

#### Visual 3 (Right Top): Match Winning Bias (Chasing vs Defending)
- **Visual Type**: Donut Chart
- **Legend**: `Fact_Matches[win_type]`
- **Values**: `[Total Matches]`
- **Data Labels**: Category & Percentage of Total

#### Visual 4 (Right Bottom): Toss-to-Match Win Conversion
- **Visual Type**: Gauge Chart
- **Value**: `[Toss Match Win Correlation %]`
- **Target**: 0.50 (50% neutral baseline)

---

### Page 2 — Batting Analytics & Powerplay Breakdown

**Goal**: Comprehensive offensive evaluation of top batters, strike rates, boundary reliance, and match phases.

#### Slicers
- **Season**: Multi-select dropdown (`Dim_Date[Year]`)
- **Player Name**: Searchable dropdown (`Dim_Player[player_name]`)
- **Franchise**: Dropdown (`Dim_Team[team_name]`)

#### Visual 1: All-Time Run Scorers (The Orange Cap Legends)
- **Visual Type**: Clustered Bar Chart
- **Y-Axis**: `Agg_BattingCareer[player_name]` (Top 10 filtered by runs)
- **X-Axis**: `Agg_BattingCareer[runs]`
- **Color Saturation**: `Agg_BattingCareer[strike_rate]`

#### Visual 2: Batting Efficiency Quadrant (Scatter Plot)
- **Visual Type**: Scatter Chart
- **X-Axis**: `Agg_BattingCareer[strike_rate]`
- **Y-Axis**: `Agg_BattingCareer[batting_average]`
- **Size**: `Agg_BattingCareer[runs]`
- **Color**: `Agg_BattingCareer[batting_impact]`
- **Details**: `Agg_BattingCareer[player_name]`
- **Visual Filter**: `Agg_BattingCareer[runs] >= 1000`

#### Visual 3: Boundary Generation vs Strike Rate
- **Visual Type**: Line and Clustered Column Chart
- **X-Axis**: `Agg_BattingCareer[player_name]` (Top 15)
- **Column Values**: `Agg_BattingCareer[fours]`, `Agg_BattingCareer[sixes]`
- **Line Values**: `Agg_BattingCareer[boundary_pct]`

#### Visual 4: Phase-by-Phase Batting Scoring Breakdown
- **Visual Type**: Matrix Visual
- **Rows**: `Agg_BattingCareer[player_name]`
- **Columns**: `Powerplay Runs`, `Middle Runs`, `Death Overs Runs`, `Death Strike Rate`

---

### Page 3 — Bowling Analytics & Wicket Intelligence

**Goal**: Defensive mastery, economy suppression, death-over clutch bowling, and dot-ball pressure.

#### Slicers
- **Season**: Dropdown (`Dim_Date[Year]`)
- **Bowler Name**: Searchable dropdown (`Dim_Player[player_name]`)
- **Match Phase**: Single-select (`Fact_BallByBall[match_phase]`)

#### Visual 1: All-Time Purple Cap Contenders (Top Wicket Takers)
- **Visual Type**: Clustered Bar Chart
- **Y-Axis**: `Agg_BowlingCareer[player_name]` (Top 10)
- **X-Axis**: `Agg_BowlingCareer[wickets]`
- **Data Labels**: Economy rate badge

#### Visual 2: Bowling Efficiency Matrix (The Golden Quadrant)
- **Visual Type**: Scatter Chart
- **X-Axis**: `Agg_BowlingCareer[economy_rate]` (Invert axis: lower on right)
- **Y-Axis**: `Agg_BowlingCareer[bowling_strike_rate]` (Invert axis: lower on top)
- **Size**: `Agg_BowlingCareer[wickets]`
- **Color**: `Agg_BowlingCareer[bowling_impact]`
- **Details**: `Agg_BowlingCareer[player_name]`
- **Filter**: `Agg_BowlingCareer[wickets] >= 50`

#### Visual 3: Dot Ball Machine (Pressure Index)
- **Visual Type**: Clustered Bar Chart
- **Y-Axis**: `Agg_BowlingCareer[player_name]` (Top 10 by Dot Ball %)
- **X-Axis**: `Agg_BowlingCareer[dot_ball_pct]`

#### Visual 4: Death-Over Execution Table
- **Visual Type**: Table / Matrix
- **Columns**: `player_name`, `death_wickets`, `death_balls`, `death_economy`

---

