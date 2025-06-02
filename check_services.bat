@echo off
REM check_services.bat - Comprehensive service debugging script
echo ==========================================
echo Campaign Manager - Service Diagnostics
echo ==========================================

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Must run as Administrator
    pause
    exit /b 1
)

echo ✅ Running as Administrator
echo.

REM Check service status
echo 📊 SERVICE STATUS:
echo.
echo Backend Service:
sc query CampaignManagerBackend
echo.
echo Frontend Service:
sc query CampaignManagerFrontend
echo.

REM Check if services are running
net start | findstr "Campaign" >nul
if %errorlevel% equ 0 (
    echo ✅ Some Campaign Manager services are running
) else (
    echo ❌ No Campaign Manager services appear to be running
)
echo.

REM Check processes
echo 📋 RUNNING PROCESSES:
echo.
echo Python processes:
tasklist /FI "IMAGENAME eq python3.10.exe" 2>nul | findstr python
if %errorlevel% neq 0 echo No Python 3.10 processes found

echo.
echo Node processes:
tasklist /FI "IMAGENAME eq node.exe" 2>nul | findstr node
if %errorlevel% neq 0 echo No Node processes found

echo.

REM Check ports
echo 🌐 PORT STATUS:
echo.
echo Port 5000 (Backend):
netstat -an | findstr ":5000"
if %errorlevel% neq 0 echo Port 5000 not in use

echo.
echo Port 3000 (Frontend):
netstat -an | findstr ":3000"
if %errorlevel% neq 0 echo Port 3000 not in use

echo.

REM Check log files
echo 📄 LOG FILES:
echo.
if exist "C:\CampaignManager\backend-stdout.log" (
    echo Backend stdout log (last 10 lines):
    echo ----------------------------------------
    powershell "Get-Content 'C:\CampaignManager\backend-stdout.log' -Tail 10"
    echo ----------------------------------------
) else (
    echo ❌ Backend stdout log not found
)

echo.
if exist "C:\CampaignManager\backend-stderr.log" (
    echo Backend stderr log (last 10 lines):
    echo ----------------------------------------
    powershell "Get-Content 'C:\CampaignManager\backend-stderr.log' -Tail 10"
    echo ----------------------------------------
) else (
    echo ❌ Backend stderr log not found
)

echo.
if exist "C:\CampaignManager\frontend-stdout.log" (
    echo Frontend stdout log (last 10 lines):
    echo ----------------------------------------
    powershell "Get-Content 'C:\CampaignManager\frontend-stdout.log' -Tail 10"
    echo ----------------------------------------
) else (
    echo ❌ Frontend stdout log not found
)

echo.
if exist "C:\CampaignManager\frontend-stderr.log" (
    echo Frontend stderr log (last 10 lines):
    echo ----------------------------------------
    powershell "Get-Content 'C:\CampaignManager\frontend-stderr.log' -Tail 10"
    echo ----------------------------------------
) else (
    echo ❌ Frontend stderr log not found
)

echo.

REM Test connectivity
echo 🧪 CONNECTIVITY TESTS:
echo.
echo Testing backend health endpoint:
curl -s http://localhost:5000/api/health
if %errorlevel% equ 0 (
    echo ✅ Backend responding
) else (
    echo ❌ Backend not responding
)

echo.
echo Testing frontend:
curl -s -I http://localhost:3000 | findstr "200\|301\|302"
if %errorlevel% equ 0 (
    echo ✅ Frontend responding
) else (
    echo ❌ Frontend not responding
)

echo.

REM Check file structure
echo 📁 FILE STRUCTURE:
echo.
if exist "C:\CampaignManager\app.py" (
    echo ✅ app.py found
) else (
    echo ❌ app.py missing
)

if exist "C:\CampaignManager\run_backend.py" (
    echo ✅ run_backend.py found
) else (
    echo ❌ run_backend.py missing
)

if exist "C:\CampaignManager\campaign-manager-frontend\serve_build.js" (
    echo ✅ serve_build.js found
) else (
    echo ❌ serve_build.js missing
)

if exist "C:\CampaignManager\campaign-manager-frontend\dist\index.html" (
    echo ✅ Frontend build found
) else (
    echo ❌ Frontend build missing
)

if exist "C:\Verificator Preturi App\assets" (
    echo ✅ Assets folder found
) else (
    echo ❌ Assets folder missing
)

echo.

REM Check database
echo 💾 DATABASE CHECK:
echo.
if exist "C:\CampaignManager\campaigns.db" (
    echo ✅ Database file found
) else (
    echo ❌ Database file missing
)

echo.
echo 📋 SUMMARY:
echo To fix login issues, check:
echo 1. Backend service logs above for errors
echo 2. Frontend service logs for connection issues
echo 3. Port 5000 and 3000 availability
echo 4. Network connectivity between frontend and backend
echo.
echo 🔧 USEFUL COMMANDS:
echo.
echo Restart services:
echo   net stop CampaignManagerBackend
echo   net stop CampaignManagerFrontend
echo   net start CampaignManagerBackend
echo   net start CampaignManagerFrontend
echo.
echo View real-time logs:
echo   powershell "Get-Content 'C:\CampaignManager\backend-stderr.log' -Wait"
echo   powershell "Get-Content 'C:\CampaignManager\frontend-stderr.log' -Wait"
echo.
echo Manual testing:
echo   cd C:\CampaignManager
echo   python3.10 run_backend.py
echo.
echo   cd C:\CampaignManager\campaign-manager-frontend
echo   node serve_build.js
echo.
pause