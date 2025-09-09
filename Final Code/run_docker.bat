@echo off
echo 🐳 YouTube Dataset Creation - Docker Runner
echo ==========================================
echo.

echo Choose an option:
echo 1. Build Docker Image
echo 2. Run YouTube Dataset Creation (Production Mode - 2.6M+ videos)
echo 3. Run with Custom Settings
echo 4. Check Docker Status
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto :build
if "%choice%"=="2" goto :youtube_prod
if "%choice%"=="3" goto :custom
if "%choice%"=="4" goto :status
goto :invalid

:build
echo.
echo 🔨 Building Docker image...
docker build -f Dockerfile.standalone -t youtube-dataset-prod .
if %errorlevel% equ 0 (
    echo ✅ Docker image built successfully!
) else (
    echo ❌ Docker build failed!
)
goto :end

:youtube_prod
echo.
echo 🚀 Starting YouTube Dataset Creation in PRODUCTION mode...
echo 📊 Dataset: datacsv.csv (2.6M+ rows)
echo ⚠️  WARNING: This will process 2.6M+ videos and may take several weeks!
echo 💾 Ensure you have at least 1TB of free disk space!
echo.
set /p confirm=Are you sure you want to continue? (Y/N): 
if /i "%confirm%"=="Y" (
    echo 🎬 Starting processing...
    docker run --rm -v "%cd%\dataset_production:/app/dataset_production" -v "%cd%\datacsv.csv:/app/datacsv.csv:ro" youtube-dataset-prod
) else (
    echo Operation cancelled.
)
goto :end

:custom
echo.
echo 🔧 Custom Docker Run Options
echo.
echo Available options:
echo 1. Run with different output directory
echo 2. Run with memory limit
echo 3. Run in background
echo.
set /p custom_choice=Enter your choice (1-3): 
if "%custom_choice%"=="1" goto :custom_output
if "%custom_choice%"=="2" goto :custom_memory
if "%custom_choice%"=="3" goto :custom_background
goto :end

:custom_output
set /p output_dir=Enter output directory path: 
echo 🎬 Starting with custom output directory: %output_dir%
docker run --rm -v "%output_dir%:/app/dataset_production" -v "%cd%\datacsv.csv:/app/datacsv.csv:ro" youtube-dataset-prod
goto :end

:custom_memory
echo 🎬 Starting with memory limit (4GB)...
docker run --rm --memory=4g -v "%cd%\dataset_production:/app/dataset_production" -v "%cd%\datacsv.csv:/app/datacsv.csv:ro" youtube-dataset-prod
goto :end

:custom_background
echo 🎬 Starting in background...
docker run -d --name youtube-dataset-bg -v "%cd%\dataset_production:/app/dataset_production" -v "%cd%\datacsv.csv:/app/datacsv.csv:ro" youtube-dataset-prod
echo ✅ Container started in background. Use 'docker logs youtube-dataset-bg' to view progress.
goto :end

:status
echo.
echo 📋 Docker Status:
docker ps -a
echo.
echo 📊 Disk Usage:
docker system df
goto :end

:invalid
echo Invalid choice. Please run the script again.
goto :end

:end
echo.
echo ✅ Operation completed!
pause
