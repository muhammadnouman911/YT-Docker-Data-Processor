#!/usr/bin/env python3
"""
Configuration file for YouTube Dataset Creation
Easily switch between TEST and PRODUCTION modes
"""

import os

# --- MODE SELECTION ---
# Change this to switch between modes:
# "TEST" = Use small dataset for testing
# "PRODUCTION" = Use full dataset for production
MODE = "PRODUCTION"  # Using full dataset (2.6M+ rows)

# --- CSV FILES ---
TEST_CSV = "avspeech_test_100.csv"      # Small test dataset (100 rows)
PRODUCTION_CSV = "datacsv.csv"          # Full production dataset (2.6M+ rows)

# --- OUTPUT DIRECTORIES ---
TEST_OUTPUT = "dataset_test"
PRODUCTION_OUTPUT = "dataset_production"

# --- CONFIGURATION ---
if MODE == "TEST":
    CSV_PATH = TEST_CSV
    OUTPUT_DIR = TEST_OUTPUT
    MAX_RETRIES = 2
    WORKERS = 1
    print("🔬 TEST MODE: Using small dataset for testing")
else:
    CSV_PATH = PRODUCTION_CSV
    OUTPUT_DIR = PRODUCTION_OUTPUT
    MAX_RETRIES = 3
    WORKERS = "auto"  # Will be set to max(1, cpu_count() - 1)
    print("🚀 PRODUCTION MODE: Using full dataset for production")

# --- COMMON SETTINGS ---
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
FACE_DIR = os.path.join(OUTPUT_DIR, "faces")
COOKIES_FILE = "cookies.txt" if os.path.exists("cookies.txt") else None
LOG_FILE = f"failed_downloads_{MODE.lower()}.log"
PROXY = None

# --- WORKER CONFIGURATION ---
if WORKERS == "auto":
    from multiprocessing import cpu_count
    WORKERS = max(1, cpu_count() - 1)

print(f"📁 CSV File: {CSV_PATH}")
print(f"📁 Output Directory: {OUTPUT_DIR}")
print(f"👥 Workers: {WORKERS}")
print(f"🔄 Max Retries: {MAX_RETRIES}")
print(f"⏰ Mode: {MODE}")
print("=" * 50)
