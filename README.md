
---

# 🚀 **YouTube Dataset Creation - Production Docker**

Effortlessly process a massive dataset of 2.6M+ YouTube videos using Docker! This production-grade pipeline extracts face images and audio files, streamlining data preparation for deep learning models and other projects.

## 🔧 **Quick Start**

1. **Check Docker Installation:**
   Run: `check_docker.bat`
   This ensures Docker is installed and running properly on your system.

2. **Start Data Processing:**
   Run: `run_docker.bat` → Select **Option 2** for full production processing.

---

## ⚡ **What This Does**

* **Input:** A CSV file `datacsv.csv` containing 2.6M+ YouTube video records.
* **Output:** A `dataset_production/` directory with:

  * **Audio**: Clean WAV files (16kHz, 16-bit)
  * **Faces**: JPG face images extracted from the videos
* **Mode:** **Production Only** (No test mode, runs continuously for optimal efficiency)
* **Processing Time:** Multiple weeks of processing time, depending on system resources and internet speed.

---

## 📂 **Expected Output Structure**

After running the pipeline, you'll find:

```
dataset_production/
├── audio/          # WAV files (16kHz, 16-bit)
└── faces/          # Face images (JPG format)
```

---

## ⚙️ **System Requirements**

Ensure your system meets the following prerequisites for optimal performance:

* **Docker:** Installed and actively running (check with `check_docker.bat`).
* **Disk Space:** 1TB+ free space (due to large video processing output).
* **Internet Connection:** Stable and fast for downloading video data.
* **Processing Time:** Be prepared for several weeks of continuous processing.

---

## 🗂️ **Files Included**

* **`Dockerfile.standalone`** – Standalone Docker container for easy setup.
* **`run_docker.bat`** – Main script to execute the processing workflow.
* **`check_docker.bat`** – Verifies that Docker is set up and functional.
* **`config.py`** – Configuration file for production mode.
* **`youtube_download_portable.py`** – Main processing script for downloading and extracting data.
* **`setup_portable.py`** – Environment setup script to ensure all dependencies are installed.
* **`requirements.txt`** – List of Python dependencies for the project.
* **`datacsv.csv`** – Your YouTube video dataset (2.6M+ rows, ready to go).

---

## 🚀 **Ready to Process 2.6M+ Videos?**

1. Ensure Docker is running.
2. Run `check_docker.bat` to verify Docker setup.
3. Run `run_docker.bat` → Select **Option 2** to start processing.

Start your journey towards creating a massive dataset now! 🎬

---
