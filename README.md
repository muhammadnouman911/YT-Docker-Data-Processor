# 🚀 YouTube Dataset Creation - Production Docker

## Quick Start

1. **Check Docker:** `check_docker.bat`
2. **Run Processing:** `run_docker.bat` → Choose option 2

## What This Does

- **Input:** `datacsv.csv` (2.6M+ YouTube videos)
- **Output:** `dataset_production/` folder with audio and face data
- **Mode:** PRODUCTION (no test mode)
- **Time:** Several weeks of continuous processing

## Expected Output

```
dataset_production/
├── audio/          # WAV files (16kHz, 16-bit)
└── faces/          # Face images (JPG format)
```

## Requirements

- Docker installed and running
- 1TB+ free disk space
- Stable internet connection
- Several weeks of processing time

## Files

- `Dockerfile.standalone` - Docker container
- `run_docker.bat` - Main runner script
- `check_docker.bat` - Docker checker
- `config.py` - Configuration (PRODUCTION mode)
- `youtube_download_portable.py` - Main processing script
- `setup_portable.py` - Environment setup
- `requirements.txt` - Python dependencies
- `datacsv.csv` - Your dataset (2.6M+ rows)

---

**Ready to process 2.6M+ videos? Run `run_docker.bat`!**
