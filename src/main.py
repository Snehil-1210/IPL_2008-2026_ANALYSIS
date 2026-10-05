"""
Cricket Analytics & Performance Intelligence System
Master Pipeline Execution Script
Runs Phases 1 through 6 sequentially with full validation.
"""

import os
import sys
import time

# Ensure src can import other modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import download_and_extract_ipl_data
from cleaner import run_cleaning_pipeline
from model_builder import build_star_schema
from features import run_feature_engineering_pipeline
from eda_visualizer import generate_all_eda_visualizations


def run_full_pipeline():
    total_start = time.time()
    print("*" * 75)
    print("CRICKET ANALYTICS SYSTEM: END-TO-END PIPELINE EXECUTION")
    print("*" * 75)

    # Phase 1: Data Acquisition
    print("\n>>> STEP 1: DATA ACQUISITION")
    download_and_extract_ipl_data()

    # Phase 2: Data Cleaning & Domain Standardization
    print("\n>>> STEP 2: DATA CLEANING & DOMAIN STANDARDIZATION")
    run_cleaning_pipeline()

    # Phase 3: Analytical Data Modeling (Star Schema)
    print("\n>>> STEP 3: DATA MODELING (STAR SCHEMA)")
    build_star_schema()

    # Phase 4 & 6: Feature Engineering & Advanced Intelligence Metrics
    print("\n>>> STEP 4: FEATURE ENGINEERING & ADVANCED METRICS")
    run_feature_engineering_pipeline()

    # Phase 5: Exploratory Data Analysis & Visualizations
    print("\n>>> STEP 5: EXPLORATORY DATA ANALYSIS & VISUALIZATIONS")
    generate_all_eda_visualizations()

    print("\n" + "*" * 75)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {time.time() - total_start:.2f} SECONDS!")
    print("Processed tables saved in: data/processed/")
    print("EDA visual assets saved in: reports/screenshots/")
    print("Power BI model guide in:    powerbi/data_model_guide.md")
    print("DAX measures library in:    powerbi/dax_measures.txt")
    print("*" * 75)


if __name__ == "__main__":
    run_full_pipeline()
