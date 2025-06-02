@echo off
REM setup_windows_services_fixed.bat - Install Campaign Manager as Windows Services
REM Run as Administrator

echo ==========================================
echo Campaign Manager - Windows Services Setup
echo ==========================================

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Must run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo ✅ Running as Administrator

REM Configuration
set SERVICE_DIR=C:\CampaignManager
set ASSETS_DIR=C:\Verificator Preturi App\assets
set PYTHON_PATH=python3.10

REM Check if Python 3.10 is installed
%PYTHON_PATH% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.10 not found. Please install Python 3.10 first.
    echo Available from Microsoft Store or https://www.python.org/downloads/
    echo.
    echo Current Python status:
    python --version 2>nul && python --version || echo python: Not found
    python3 --version 2>nul && python3 --version || echo python3: Not found
    python3.10 --version 2>nul && python3.10 --version || echo python3.10: Not found
    pause
    exit /b 1
)

echo ✅ Python 3.10 found: 
%PYTHON_PATH% --version

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js found:
node --version

REM Create service directory
echo 📁 Creating service directory...
if not exist "%SERVICE_DIR%" mkdir "%SERVICE_DIR%"

REM Copy application files
echo 📂 Copying application files...
xcopy /E /I /Y "%~dp0*" "%SERVICE_DIR%\"

REM Create assets directory if it doesn't exist
if not exist "%ASSETS_DIR%" (
    echo 📁 Creating assets directory...
    mkdir "%ASSETS_DIR%"
) else (
    echo ✅ Assets directory already exists: %ASSETS_DIR%
)

REM Install Python dependencies with python3.10
echo 🐍 Installing Python dependencies with Python 3.10...
cd /d "%SERVICE_DIR%"
%PYTHON_PATH% -m pip install --upgrade pip
%PYTHON_PATH% -m pip install -r requirements.txt

REM Install additional Windows service dependencies
echo 📦 Installing additional service dependencies...
%PYTHON_PATH% -m pip install pywin32 waitress

REM Test Flask installation
echo 🧪 Testing Flask installation...
%PYTHON_PATH% -c "
try:
    import flask
    import flask_cors
    print('✅ Flask and dependencies installed successfully!')
    print('Flask version:', flask.__version__)
except ImportError as e:
    print('❌ Import error:', e)
    exit(1)
"

if %errorlevel% neq 0 (
    echo ❌ Flask installation failed. Please check dependencies.
    pause
    exit /b 1
)

REM Fix PostCSS configuration for Windows
echo 🔧 Fixing PostCSS configuration...
cd /d "%SERVICE_DIR%\campaign-manager-frontend"
echo module.exports = { > postcss.config.js
echo   plugins: { >> postcss.config.js
echo     tailwindcss: {}, >> postcss.config.js
echo     autoprefixer: {}, >> postcss.config.js
echo   }, >> postcss.config.js
echo } >> postcss.config.js

REM Update package.json to include express dependencies
echo 📦 Installing frontend dependencies...
call npm install
call npm install express http-proxy-middleware

REM Build React frontend
echo ⚛️ Building React frontend...
call npm run build

if %errorlevel% neq 0 (
    echo ❌ Frontend build failed. Checking for issues...
    echo Trying to fix and rebuild...
    
    REM Try to fix common build issues
    call npm install --legacy-peer-deps
    call npm run build
    
    if %errorlevel% neq 0 (
        echo ❌ Frontend build still failing. Please check the errors above.
        echo You can continue with backend setup and fix frontend later.
        set /p continue=Continue anyway? (y/n): 
        if /i not "!continue!"=="y" exit /b 1
    )
)

REM Create production environment file
echo 🔧 Creating production environment...
echo VITE_API_URL=http://192.168.103.111:5000 > .env.production

REM Initialize database with python3.10
echo 💾 Initializing database...
cd /d "%SERVICE_DIR%"
%PYTHON_PATH% scripts\init_db.py

if %errorlevel% neq 0 (
    echo ❌ Database initialization failed.
    pause
    exit /b 1
)

%PYTHON_PATH% scripts\setup_admin.py

if %errorlevel% neq 0 (
    echo ❌ Admin setup failed.
    pause
    exit /b 1
)

echo ✅ Database and admin setup complete!

REM Install services using NSSM (Non-Sucking Service Manager)
echo 📥 Downloading NSSM (Service Manager)...
powershell -Command "& {
    try {
        Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'
        Expand-Archive -Path 'nssm.zip' -DestinationPath '.' -Force
        Copy-Item '.\nssm-2.24\win64\nssm.exe' '.\nssm.exe' -Force
        Write-Host '✅ NSSM downloaded successfully'
    } catch {
        Write-Host '❌ Failed to download NSSM:' $_.Exception.Message
        exit 1
    }
}"

if %errorlevel% neq 0 (
    echo ❌ Failed to download NSSM. Please download manually from https://nssm.cc/
    pause
    exit /b 1
)

REM Remove existing services if they exist
echo 🧹 Cleaning up existing services...
net stop CampaignManagerBackend 2>nul
net stop CampaignManagerFrontend 2>nul
.\nssm.exe remove CampaignManagerBackend confirm 2>nul
.\nssm.exe remove CampaignManagerFrontend confirm 2>nul

echo 🔧 Installing Backend Service with Python 3.10...
.\nssm.exe install CampaignManagerBackend "%PYTHON_PATH%" "%SERVICE_DIR%\run_backend.py"
.\nssm.exe set CampaignManagerBackend AppDirectory "%SERVICE_DIR%"
.\nssm.exe set CampaignManagerBackend DisplayName "Campaign Manager Backend"
.\nssm.exe set CampaignManagerBackend Description "Campaign Manager Flask Backend Service (Python 3.10)"
.\nssm.exe set CampaignManagerBackend Start SERVICE_AUTO_START

echo 🔧 Installing Frontend Service...
.\nssm.exe install CampaignManagerFrontend "node" "%SERVICE_DIR%\campaign-manager-frontend\serve_build.js"
.\nssm.exe set CampaignManagerFrontend AppDirectory "%SERVICE_DIR%\campaign-manager-frontend"
.\nssm.exe set CampaignManagerFrontend DisplayName "Campaign Manager Frontend"
.\nssm.exe set CampaignManagerFrontend Description "Campaign Manager React Frontend Service"
.\nssm.exe set CampaignManagerFrontend Start SERVICE_AUTO_START

echo ▶️ Starting services...
echo Starting backend service...
net start CampaignManagerBackend

if %errorlevel% neq 0 (
    echo ❌ Backend service failed to start. Checking logs...
    .\nssm.exe status CampaignManagerBackend
    echo.
    echo You can check detailed logs with: 
    echo services.msc (look for Campaign Manager Backend)
    echo.
    echo Testing backend manually...
    echo Press Ctrl+C to stop when you see it working:
    %PYTHON_PATH% run_backend.py
) else (
    echo ✅ Backend service started successfully
)

echo Starting frontend service...
net start CampaignManagerFrontend

if %errorlevel% neq 0 (
    echo ❌ Frontend service failed to start. You can start it manually later.
) else (
    echo ✅ Frontend service started successfully
)

REM Configure Windows Firewall
echo 🛡️ Configuring firewall...
netsh advfirewall firewall add rule name="Campaign Manager Backend" dir=in action=allow protocol=TCP localport=5000 2>nul
netsh advfirewall firewall add rule name="Campaign Manager Frontend" dir=in action=allow protocol=TCP localport=3000 2>nul

echo ✅ Windows Services Installation Complete!
echo.
echo 🌐 Your application should be available at:
echo    Frontend: http://192.168.103.111:3000
echo    Backend:  http://192.168.103.111:5000
echo    Health:   http://192.168.103.111:5000/api/health
echo.
echo 🧪 Testing connectivity...
timeout /t 5 /nobreak >nul
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is responding
) else (
    echo ⚠️ Backend not responding yet - may need more time to start
)

curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is responding
) else (
    echo ⚠️ Frontend not responding yet
)

echo.
echo 🔧 Service Management Commands:
echo    Check Status:    services.msc
echo    Start Backend:   net start CampaignManagerBackend
echo    Stop Backend:    net stop CampaignManagerBackend
echo    Start Frontend:  net start CampaignManagerFrontend
echo    Stop Frontend:   net stop CampaignManagerFrontend
echo    Backend Logs:    .\nssm.exe status CampaignManagerBackend
echo.
echo 📁 Campaign files will be created in: %ASSETS_DIR%
echo.
echo 🚀 Setup complete! Try accessing the application now.
echo.
pause