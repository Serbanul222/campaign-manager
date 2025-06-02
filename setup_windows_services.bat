@echo off
REM setup_windows_services.bat - Install Campaign Manager as Windows Services
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
set PYTHON_PATH=python

REM Check if Python is installed
%PYTHON_PATH% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js found

REM Create service directory
echo 📁 Creating service directory...
if not exist "%SERVICE_DIR%" mkdir "%SERVICE_DIR%"

REM Copy application files
echo 📂 Copying application files...
xcopy /E /I /Y "%~dp0*" "%SERVICE_DIR%\"

REM Create assets directory if it doesn't exist
if not exist "%ASSETS_DIR%" mkdir "%ASSETS_DIR%"

REM Install Python dependencies
echo 🐍 Installing Python dependencies...
cd /d "%SERVICE_DIR%"
%PYTHON_PATH% -m pip install -r requirements.txt

REM Install additional Windows service dependencies
%PYTHON_PATH% -m pip install pywin32 waitress

REM Build React frontend
echo ⚛️ Building React frontend...
cd /d "%SERVICE_DIR%\campaign-manager-frontend"
call npm install
call npm run build

REM Create production environment file
echo 🔧 Creating production environment...
echo VITE_API_URL=http://192.168.103.111:5000 > .env.production

REM Initialize database
echo 💾 Initializing database...
cd /d "%SERVICE_DIR%"
%PYTHON_PATH% scripts\init_db.py
%PYTHON_PATH% scripts\setup_admin.py

echo ✅ Setup complete! Now installing Windows services...

REM Install services using NSSM (Non-Sucking Service Manager)
echo 📥 Downloading NSSM (Service Manager)...
powershell -Command "& {Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'; Expand-Archive -Path 'nssm.zip' -DestinationPath '.'; Copy-Item '.\nssm-2.24\win64\nssm.exe' '.\nssm.exe'}"

echo 🔧 Installing Backend Service...
.\nssm.exe install CampaignManagerBackend "%PYTHON_PATH%" "%SERVICE_DIR%\run_backend.py"
.\nssm.exe set CampaignManagerBackend AppDirectory "%SERVICE_DIR%"
.\nssm.exe set CampaignManagerBackend DisplayName "Campaign Manager Backend"
.\nssm.exe set CampaignManagerBackend Description "Campaign Manager Flask Backend Service"
.\nssm.exe set CampaignManagerBackend Start SERVICE_AUTO_START

echo 🔧 Installing Frontend Service...
.\nssm.exe install CampaignManagerFrontend "node" "%SERVICE_DIR%\campaign-manager-frontend\serve_build.js"
.\nssm.exe set CampaignManagerFrontend AppDirectory "%SERVICE_DIR%\campaign-manager-frontend"
.\nssm.exe set CampaignManagerFrontend DisplayName "Campaign Manager Frontend"
.\nssm.exe set CampaignManagerFrontend Description "Campaign Manager React Frontend Service"
.\nssm.exe set CampaignManagerFrontend Start SERVICE_AUTO_START

echo ▶️ Starting services...
net start CampaignManagerBackend
net start CampaignManagerFrontend

REM Configure Windows Firewall
echo 🛡️ Configuring firewall...
netsh advfirewall firewall add rule name="Campaign Manager Backend" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="Campaign Manager Frontend" dir=in action=allow protocol=TCP localport=3000

echo ✅ Windows Services Installation Complete!
echo.
echo 🌐 Your application is now available at:
echo    Frontend: http://192.168.103.111:3000
echo    Backend:  http://192.168.103.111:5000
echo    Health:   http://192.168.103.111:5000/api/health
echo.
echo 🔧 Service Management:
echo    Start Backend:   net start CampaignManagerBackend
echo    Stop Backend:    net stop CampaignManagerBackend
echo    Start Frontend:  net start CampaignManagerFrontend
echo    Stop Frontend:   net stop CampaignManagerFrontend
echo.
echo 📊 Check Service Status:
echo    services.msc (look for Campaign Manager services)
echo.
echo 📁 Files will be created in: %ASSETS_DIR%
echo.
pause