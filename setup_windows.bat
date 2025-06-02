@echo off
REM Setup script for Campaign Manager on Windows VM
REM This script is specifically for the Windows VM branch
REM Your localhost development setup remains unchanged
REM 
REM Run this script as Administrator

echo ==========================================
echo Campaign Manager - Windows VM Setup
echo IP: 192.168.103.111
echo ==========================================
echo.

REM Check if we're running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo ✅ Running as Administrator

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running or not installed
    echo Please install Docker Desktop and make sure it's running
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Navigate to the project directory
cd /d "%~dp0"
echo 📍 Current directory: %CD%

REM Check if we're in a git repository and on the right branch
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Not in a git repository
) else (
    echo ✅ Git repository detected
    for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
    echo 📍 Current branch: %CURRENT_BRANCH%
)

REM Check if assets folder exists
if not exist "C:\Verificator Preturi App\assets" (
    echo ERROR: Assets folder not found at C:\Verificator Preturi App\assets
    echo Please create this folder first or update the path in docker-compose-windows.yml
    pause
    exit /b 1
)

echo ✅ Assets folder found: C:\Verificator Preturi App\assets

REM Check if Windows-specific config files exist
if not exist "docker-compose-windows.yml" (
    echo ERROR: docker-compose-windows.yml not found
    echo Make sure you're on the Windows VM branch with all config files
    pause
    exit /b 1
)

if not exist "campaign-manager-frontend\vite.config-windows.js" (
    echo ERROR: vite.config-windows.js not found
    echo Make sure you're on the Windows VM branch with all config files
    pause
    exit /b 1
)

if not exist "campaign-manager-frontend\.env.windows" (
    echo ERROR: .env.windows not found
    echo Make sure you're on the Windows VM branch with all config files
    pause
    exit /b 1
)

echo ✅ All Windows-specific config files found

REM Stop any existing containers
echo.
echo 🛑 Stopping any existing containers...
docker-compose -f docker-compose-windows.yml down 2>nul

REM Clean up any existing images (optional - uncomment if you want to rebuild everything)
REM docker system prune -f

REM Build and start the containers
echo.
echo 🚀 Building and starting containers for Windows VM...
echo This may take a few minutes on first run...
echo.

docker-compose -f docker-compose-windows.yml up --build -d

if %errorlevel% neq 0 (
    echo ERROR: Failed to start containers
    echo.
    echo Troubleshooting:
    echo 1. Check if ports 5000 and 5173 are available
    echo 2. Make sure Docker Desktop is running
    echo 3. Verify the assets folder path exists
    echo.
    echo To see detailed logs, run:
    echo docker-compose -f docker-compose-windows.yml logs
    pause
    exit /b 1
)

REM Wait a moment for containers to fully start
echo.
echo ⏳ Waiting for containers to start...
timeout /t 10 /nobreak >nul

REM Check container status
echo.
echo 📊 Container Status:
docker-compose -f docker-compose-windows.yml ps

echo.
echo ✅ Containers started successfully!
echo.
echo 🌐 Access URLs (from any device on your network):
echo    Frontend:    http://192.168.103.111:5173
echo    Backend API: http://192.168.103.111:5000
echo    Health Check: http://192.168.103.111:5000/api/health
echo.
echo 💻 Local access (from this VM):
echo    Frontend:    http://localhost:5173
echo    Backend API: http://localhost:5000
echo.
echo 🎯 Next Steps:
echo 1. Open http://192.168.103.111:5173 in your browser
echo 2. Login with: serban.damian@lensa.ro
echo 3. Set your password (first time login)
echo 4. Create campaigns - folders will be created automatically!
echo.
echo 📁 Campaign folders will be created in: C:\Verificator Preturi App\assets
echo.
echo 🔧 Management Commands:
echo    Stop:      docker-compose -f docker-compose-windows.yml down
echo    Logs:      docker-compose -f docker-compose-windows.yml logs -f
echo    Restart:   docker-compose -f docker-compose-windows.yml restart
echo    Status:    docker-compose -f docker-compose-windows.yml ps
echo.

REM Test the connection
echo 🧪 Testing connection...
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is responding
) else (
    echo ⚠️ Backend not responding yet, may need more time to start
)

echo.
echo 🎉 Setup complete! 
echo The application should now be accessible from any device on your network.
echo.
pause