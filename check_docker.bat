@echo off
echo 🔍 Checking Docker Installation
echo ================================
echo.

echo Checking if Docker is installed...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker is installed and accessible
    docker --version
    echo.
    echo Checking if Docker daemon is running...
    docker ps >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Docker daemon is running
        echo.
        echo 🚀 Ready to build and run containers!
        echo.
        echo Next steps:
        echo 1. Run: run_docker.bat
        echo 2. Choose option 1 to build the image
        echo 3. Choose option 2 to start processing
    ) else (
        echo ❌ Docker daemon is not running
        echo.
        echo Please start Docker Desktop or Docker daemon
        echo Then run this script again
    )
) else (
    echo ❌ Docker is not installed or not in PATH
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    echo After installation:
    echo 1. Start Docker Desktop
    echo 2. Run this script again
)

echo.
pause
