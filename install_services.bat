@echo off
REM install_services.bat - Install Campaign Manager as Windows Services
echo ==========================================
echo Campaign Manager - Service Installation
echo ==========================================

REM Check admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Must run as Administrator
    pause
    exit /b 1
)

echo ✅ Running as Administrator

REM Check if setup was completed
if not exist "C:\CampaignManager\app.py" (
    echo ❌ Setup not completed - run simple_debug.bat first
    pause
    exit /b 1
)

if not exist "C:\CampaignManager\run_backend.py" (
    echo ❌ run_backend.py not found - run simple_debug.bat first
    pause
    exit /b 1
)

if not exist "C:\CampaignManager\campaign-manager-frontend\serve_build.js" (
    echo ❌ serve_build.js not found - run simple_debug.bat first
    pause
    exit /b 1
)

echo ✅ All required files found

cd C:\CampaignManager

REM Download NSSM if needed
if not exist nssm.exe (
    echo 📥 Downloading NSSM...
    powershell -Command "try { Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'; Expand-Archive -Path 'nssm.zip' -DestinationPath '.'; Copy-Item '.\nssm-2.24\win64\nssm.exe' '.\nssm.exe'; Write-Host 'NSSM downloaded' } catch { Write-Host 'Download failed' }"
)

REM Remove existing services
echo 🧹 Cleaning up existing services...
net stop "Campaign Manager Backend" 2>nul
net stop "Campaign Manager Frontend" 2>nul
net stop CampaignManagerBackend 2>nul
net stop CampaignManagerFrontend 2>nul

.\nssm.exe remove "Campaign Manager Backend" confirm 2>nul
.\nssm.exe remove "Campaign Manager Frontend" confirm 2>nul
.\nssm.exe remove CampaignManagerBackend confirm 2>nul
.\nssm.exe remove CampaignManagerFrontend confirm 2>nul

echo ✅ Cleanup completed

REM Install Backend Service
echo 🔧 Installing Backend Service...
.\nssm.exe install CampaignManagerBackend "C:\Users\Verificator Preturi\AppData\Local\Microsoft\WindowsApps\python3.10.exe" "C:\CampaignManager\run_backend.py"
.\nssm.exe set CampaignManagerBackend AppDirectory "C:\CampaignManager"
.\nssm.exe set CampaignManagerBackend DisplayName "Campaign Manager Backend"
.\nssm.exe set CampaignManagerBackend Description "Campaign Manager Flask Backend Service"
.\nssm.exe set CampaignManagerBackend Start SERVICE_AUTO_START
.\nssm.exe set CampaignManagerBackend AppStdout "C:\CampaignManager\backend-stdout.log"
.\nssm.exe set CampaignManagerBackend AppStderr "C:\CampaignManager\backend-stderr.log"

REM Install Frontend Service
echo 🔧 Installing Frontend Service...
.\nssm.exe install CampaignManagerFrontend "node" "C:\CampaignManager\campaign-manager-frontend\serve_build.js"
.\nssm.exe set CampaignManagerFrontend AppDirectory "C:\CampaignManager\campaign-manager-frontend"
.\nssm.exe set CampaignManagerFrontend DisplayName "Campaign Manager Frontend"
.\nssm.exe set CampaignManagerFrontend Description "Campaign Manager React Frontend Service"
.\nssm.exe set CampaignManagerFrontend Start SERVICE_AUTO_START
.\nssm.exe set CampaignManagerFrontend AppStdout "C:\CampaignManager\frontend-stdout.log"
.\nssm.exe set CampaignManagerFrontend AppStderr "C:\CampaignManager\frontend-stderr.log"

REM Configure Windows Firewall
echo 🛡️ Configuring firewall...
netsh advfirewall firewall add rule name="Campaign Manager Backend" dir=in action=allow protocol=TCP localport=5000 2>nul
netsh advfirewall firewall add rule name="Campaign Manager Frontend" dir=in action=allow protocol=TCP localport=3000 2>nul

REM Start services
echo ▶️ Starting services...
echo Starting backend...
net start CampaignManagerBackend
if %errorlevel% neq 0 (
    echo ❌ Backend service failed to start
    echo Checking error logs...
    type C:\CampaignManager\backend-stderr.log
    pause
) else (
    echo ✅ Backend service started
)

echo Starting frontend...
net start CampaignManagerFrontend
if %errorlevel% neq 0 (
    echo ❌ Frontend service failed to start
    echo Checking error logs...
    type C:\CampaignManager\frontend-stderr.log
    pause
) else (
    echo ✅ Frontend service started
)

REM Test services
echo 🧪 Testing services...
timeout /t 5 /nobreak >nul

curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is responding
) else (
    echo ⚠️ Backend not responding yet
)

curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is responding
) else (
    echo ⚠️ Frontend not responding yet
)

echo.
echo ✅ SERVICES INSTALLATION COMPLETE!
echo.
echo 🌐 Your application is available at:
echo    Frontend: http://192.168.103.111:3000
echo    Backend:  http://192.168.103.111:5000/api/health
echo.
echo 👤 Login with:
echo    Email: serban.damian@lensa.ro
echo    Password: Set on first login
echo.
echo 🔧 Service Management:
echo    services.msc - View/manage services
echo    net start CampaignManagerBackend
echo    net stop CampaignManagerBackend
echo    net start CampaignManagerFrontend
echo    net stop CampaignManagerFrontend
echo.
echo 📁 Campaign files will be created in:
echo    C:\Verificator Preturi App\assets
echo.
pause