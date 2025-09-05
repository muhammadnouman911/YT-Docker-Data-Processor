#!/usr/bin/env python3
"""
YouTube Dataset Creation - PORTABLE VERSION
Automatically runs in TEST or PRODUCTION mode based on config.py
Can be easily transferred to any PC (CPU or GPU) and run immediately
"""

import os
import cv2
import pandas as pd
import yt_dlp
import ffmpeg
from tqdm import tqdm
import time
import shutil
from multiprocessing import Pool, cpu_count
import zipfile
from datetime import datetime, timedelta
import sys

# Import configuration
from config import *

# Ensure UTF-8 encoding for all output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
    sys.stderr.reconfigure(encoding="utf-8", errors="ignore")

# Create output directories
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(FACE_DIR, exist_ok=True)

print(f"🚀 Starting YouTube Dataset Creation")
print(f"📁 Processing: {CSV_PATH}")
print(f"📁 Output: {OUTPUT_DIR}")
print(f"👥 Workers: {WORKERS}")
print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"💾 Auto-cleanup: ENABLED (saves disk space)")

# --- Enhanced Logging ---
def log_failure(youtube_id, reason, details=""):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{youtube_id},{reason},{details}\n")

# --- Progress Tracking Class ---
class ProgressTracker:
    def __init__(self, total_items):
        self.total_items = total_items
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()
        self.current_item = 0
        self.last_update_time = time.time()
        
    def update(self, success=True):
        self.current_item += 1
        if success:
            self.completed += 1
        else:
            self.failed += 1
        
        # Update progress every 10 items or every 30 seconds
        current_time = time.time()
        if (self.current_item % 10 == 0) or (current_time - self.last_update_time > 30):
            self._show_progress_update()
            self.last_update_time = current_time
    
    def _show_progress_update(self):
        # Calculate progress
        progress_percent = (self.current_item / self.total_items) * 100
        elapsed_time = time.time() - self.start_time
        
        if self.current_item > 0:
            # Estimate remaining time
            avg_time_per_item = elapsed_time / self.current_item
            remaining_items = self.total_items - self.current_item
            estimated_remaining = avg_time_per_item * remaining_items
            
            # Format time estimates
            elapsed_str = str(timedelta(seconds=int(elapsed_time)))
            remaining_str = str(timedelta(seconds=int(estimated_remaining)))
            
            # Calculate success rate
            success_rate = (self.completed / self.current_item) * 100 if self.current_item > 0 else 0
            
            # Calculate speed
            speed_per_hour = self.current_item / elapsed_time * 3600 if elapsed_time > 0 else 0
            
            print(f"\n📊 PROGRESS UPDATE #{self.current_item:,}/{self.total_items:,}")
            print(f"   🎯 Completion: {progress_percent:.1f}% ({self.current_item:,}/{self.total_items:,})")
            print(f"   ✅ Success: {self.completed:,} | ❌ Failed: {self.failed:,}")
            print(f"   📈 Success Rate: {success_rate:.1f}%")
            print(f"   ⏱️  Elapsed: {elapsed_str} | ⏳ Remaining: {remaining_str}")
            print(f"   🚀 Speed: {speed_per_hour:.1f} items/hour")
            print(f"   💾 Disk Space: Audio={len(os.listdir(AUDIO_DIR)):,} | Faces={len(os.listdir(FACE_DIR)):,}")
            print("   " + "=" * 60)

# --- Enhanced Video Download ---
def download_video(youtube_id, output_path, retry=0):
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "quiet": True,
        "ignoreerrors": True,
        "extractor_args": {"youtube": {"skip": ["hls", "dash"]}},
        "socket_timeout": 60,
        "retries": 5,
        "noplaylist": True,
        "age_limit": 0,
        "extract_flat": False,
        "no_warnings": False,
        "verbose": False,
        "extractor_retries": 3,
        "fragment_retries": 3,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    }

    if COOKIES_FILE:
        ydl_opts["cookiefile"] = COOKIES_FILE
    if PROXY:
        ydl_opts["proxy"] = PROXY

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={youtube_id}",
                download=True
            )
            if info is None:
                raise Exception("Video info not available")
        return os.path.exists(output_path)
    except Exception as e:
        error_str = str(e).lower()
        if retry < MAX_RETRIES:
            if any(x in error_str for x in ["age", "inappropriate", "sign in"]):
                # Special handling for age verification
                time.sleep(2 ** retry)
                return download_video(youtube_id, output_path, retry + 1)
            else:
                time.sleep(2 ** retry)
                return download_video(youtube_id, output_path, retry + 1)
        log_failure(youtube_id, "Download failed", str(e))
        return False

# --- Audio Extraction ---
def extract_audio(video_path, audio_path):
    try:
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(stream, audio_path, acodec='pcm_s16le', ar=16000)
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        return os.path.exists(audio_path)
    except Exception as e:
        print(f"❌ Audio extraction failed: {e}")
        return False

# --- Face Detection and Extraction ---
def extract_faces(video_path, face_dir, youtube_id):
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        frame_count = 0
        faces_found = 0
        
        while cap.isOpened() and faces_found < 10:  # Extract up to 10 faces
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % 30 != 0:  # Process every 30th frame
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in faces:
                face_img = frame[y:y+h, x:x+w]
                face_path = os.path.join(face_dir, f"{youtube_id}_face_{faces_found}.jpg")
                cv2.imwrite(face_path, face_img)
                faces_found += 1
                if faces_found >= 10:
                    break
        
        cap.release()
        return faces_found > 0
    except Exception as e:
        print(f"❌ Face extraction failed: {e}")
        return False

# --- Main Processing Function ---
def process_video(args):
    youtube_id, start_time, end_time = args
    
    # Create output paths
    video_filename = f"{youtube_id}_full.mp4"
    audio_filename = f"{youtube_id}_audio.wav"
    face_dir = os.path.join(FACE_DIR, youtube_id)
    
    video_path = os.path.join(OUTPUT_DIR, video_filename)
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    
    # Create face directory
    os.makedirs(face_dir, exist_ok=True)
    
    try:
        # Download video
        if not download_video(youtube_id, video_path):
            return False
        
        # Extract audio
        if not extract_audio(video_path, audio_path):
            return False
        
        # Extract faces
        if not extract_faces(video_path, face_dir, youtube_id):
            return False
        
        # Clean up video file to save space
        if os.path.exists(video_path):
            os.remove(video_path)
        
        return True
        
    except Exception as e:
        log_failure(youtube_id, "Processing failed", str(e))
        return False

# --- Main Execution ---
def main():
    # Check if CSV file exists
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: CSV file '{CSV_PATH}' not found!")
        print("Please ensure the CSV file is in the same directory as this script.")
        return
    
    # Load CSV data
    try:
        df = pd.read_csv(CSV_PATH)
        total_videos = len(df)
        print(f"📊 Loaded {total_videos:,} videos from {CSV_PATH}")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Prepare data for processing
    data = []
    for _, row in df.iterrows():
        youtube_id = row['youtube_id']
        start_time = row.get('start_time', 0)
        end_time = row.get('end_time', 0)
        data.append((youtube_id, start_time, end_time))
    
    # Initialize progress tracker
    progress = ProgressTracker(total_videos)
    
    print(f"🚀 Starting processing with {WORKERS} worker(s)...")
    print("=" * 60)
    
    # Process videos
    if WORKERS == 1:
        # Single-threaded processing
        for i, video_data in enumerate(data):
            success = process_video(video_data)
            progress.update(success)
            
            if i % 10 == 0:
                print(f"Processing: {i+1}/{total_videos}")
    else:
        # Multi-threaded processing
        with Pool(WORKERS) as pool:
            results = []
            for video_data in data:
                result = pool.apply_async(process_video, (video_data,))
                results.append(result)
            
            for i, result in enumerate(results):
                success = result.get()
                progress.update(success)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 PROCESSING COMPLETE!")
    print(f"📊 Total Processed: {total_videos:,}")
    print(f"✅ Successful: {progress.completed:,}")
    print(f"❌ Failed: {progress.failed:,}")
    print(f"📈 Success Rate: {progress.completed/total_videos*100:.1f}%")
    print(f"💾 Audio Files: {len(os.listdir(AUDIO_DIR)):,}")
    print(f"👥 Face Images: {len(os.listdir(FACE_DIR)):,}")
    print(f"⏱️  Total Time: {str(timedelta(seconds=int(time.time() - progress.start_time))}")
    print("=" * 60)

if __name__ == "__main__":
    main()
