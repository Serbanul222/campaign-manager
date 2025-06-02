@echo off
setlocal enabledelayedexpansion

REM setup_windows_services_debug.bat - Debug version with error handling
REM Run as Administrator

echo ==========================================
echo Campaign Manager - Windows Services Setup (DEBUG)
echo ==========================================

REM Prevent script from closing on errors
set "ErrorFound=0"

REM Function to handle errors
:HandleError
echo.
echo ❌ ERROR at line %1: %2
set "ErrorFound=1"
echo Press any key to continue anyway, or Ctrl+C to stop...
pause >nul
goto :eof

REM Check if running as admin
echo 🔍 Checking administrator privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Must run as Administrator
    echo Right-click and select "Run as administrator"
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo ✅ Running as Administrator

REM Configuration
echo 🔧 Setting up configuration...
set "SERVICE_DIR=C:\CampaignManager"
set "ASSETS_DIR=C:\Verificator Preturi App\assets"
set "PYTHON_PATH=python3.10"
echo Service Directory: %SERVICE_DIR%
echo Assets Directory: %ASSETS_DIR%
echo Python Path: %PYTHON_PATH%

REM Check current directory
echo.
echo 📍 Current directory: %CD%
echo 📁 Contents:
dir /b | findstr /i "app.py" >nul && echo ✅ app.py found || echo ❌ app.py not found
dir /b | findstr /i "requirements.txt" >nul && echo ✅ requirements.txt found || echo ❌ requirements.txt not found
dir /b | findstr /i "campaign-manager-frontend" >nul && echo ✅ frontend folder found || echo ❌ frontend folder not found

REM Check if Python 3.10 is installed
echo.
echo 🐍 Checking Python 3.10...
%PYTHON_PATH% --version >nul 2>&1
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Python 3.10 not found"
    echo Available Python versions:
    python --version 2>nul && echo python: && python --version || echo python: Not found
    python3 --version 2>nul && echo python3: && python3 --version || echo python3: Not found
    python3.10 --version 2>nul && echo python3.10: && python3.10 --version || echo python3.10: Not found
    echo.
    echo Please ensure Python 3.10 is installed and available as 'python3.10'
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo ✅ Python 3.10 found: 
%PYTHON_PATH% --version

REM Check if Node.js is installed
echo.
echo 🟢 Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Node.js not found"
    echo Please install Node.js from https://nodejs.org/
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo ✅ Node.js found:
node --version

REM Create service directory
echo.
echo 📁 Creating service directory...
if not exist "%SERVICE_DIR%" (
    mkdir "%SERVICE_DIR%"
    if %errorlevel% neq 0 (
        call :HandleError %LINENO% "Failed to create service directory"
        exit /b 1
    )
    echo ✅ Created: %SERVICE_DIR%
) else (
    echo ✅ Directory already exists: %SERVICE_DIR%
)

REM Copy application files
echo.
echo 📂 Copying application files...
echo From: %~dp0
echo To: %SERVICE_DIR%\
xcopy /E /I /Y /Q "%~dp0*" "%SERVICE_DIR%\"
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Failed to copy application files"
    echo Source directory: %~dp0
    echo Target directory: %SERVICE_DIR%\
    echo Error level: %errorlevel%
)

REM Check assets directory
echo.
echo 📁 Checking assets directory...
if not exist "%ASSETS_DIR%" (
    echo Creating assets directory...
    mkdir "%ASSETS_DIR%"
    if %errorlevel% neq 0 (
        call :HandleError %LINENO% "Failed to create assets directory"
    )
) else (
    echo ✅ Assets directory already exists: %ASSETS_DIR%
)

REM Change to service directory
echo.
echo 📂 Changing to service directory...
cd /d "%SERVICE_DIR%"
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Failed to change to service directory"
    exit /b 1
)
echo ✅ Working directory: %CD%

REM Check if requirements.txt exists
echo.
echo 📋 Checking requirements.txt...
if not exist "requirements.txt" (
    call :HandleError %LINENO% "requirements.txt not found in service directory"
    echo Contents of service directory:
    dir /b
    echo Press any key to continue...
    pause >nul
    exit /b 1
)
echo ✅ requirements.txt found

REM Install Python dependencies
echo.
echo 🐍 Installing Python dependencies...
echo Running: %PYTHON_PATH% -m pip install --upgrade pip
%PYTHON_PATH% -m pip install --upgrade pip
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Failed to upgrade pip"
)

echo.
echo Running: %PYTHON_PATH% -m pip install -r requirements.txt
%PYTHON_PATH% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Failed to install requirements"
    echo Contents of requirements.txt:
    type requirements.txt
    echo.
    echo Trying individual installations...
    %PYTHON_PATH% -m pip install Flask Flask-SQLAlchemy Flask-CORS
    %PYTHON_PATH% -m pip install python-dotenv PyJWT Werkzeug bcrypt Pillow
)

echo.
echo 📦 Installing service dependencies...
%PYTHON_PATH% -m pip install pywin32 waitress
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Failed to install service dependencies"
)

REM Test Flask installation
echo.
echo 🧪 Testing Flask installation...
%PYTHON_PATH% -c "import flask; print('Flask version:', flask.__version__)" 2>nul
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Flask import test failed"
    echo Trying to diagnose...
    %PYTHON_PATH% -c "import sys; print('Python path:', sys.path)"
    %PYTHON_PATH% -m pip list | findstr -i flask
)

echo.
echo ✅ Python setup complete! Press any key to continue with frontend setup...
pause >nul

REM Frontend setup
echo.
echo 🔧 Setting up frontend...
cd /d "%SERVICE_DIR%\campaign-manager-frontend"
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Frontend directory not found"
    echo Contents of service directory:
    cd /d "%SERVICE_DIR%"
    dir /b
    echo Press any key to continue...
    pause >nul
    exit /b 1
)

echo ✅ In frontend directory: %CD%

REM Fix PostCSS configuration
echo.
echo 🔧 Fixing PostCSS configuration...
(
echo module.exports = {
echo   plugins: {
echo     tailwindcss: {},
echo     autoprefixer: {},
echo   },
echo }
) > postcss.config.js
echo ✅ PostCSS config updated

REM Install frontend dependencies
echo.
echo 📦 Installing frontend dependencies...
call npm install
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "npm install failed"
    echo Trying with --legacy-peer-deps...
    call npm install --legacy-peer-deps
)

echo.
echo 📦 Installing express dependencies...
call npm install express http-proxy-middleware
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Failed to install express dependencies"
)

echo.
echo ✅ Frontend dependencies installed! Press any key to continue with build...
pause >nul

REM Build frontend
echo.
echo ⚛️ Building React frontend...
call npm run build
if %errorlevel% neq 0 (
    call :HandleError %LINENO% "Frontend build failed"
    echo Build error occurred. Check the output above.
    echo Press any key to continue anyway...
    pause >nul
)

echo.
echo ✅ Build process completed! Press any key to continue with database setup...
pause >nul

REM Database setup
echo.
echo 💾 Setting up database...
cd /d "%SERVICE_DIR%"
echo Current directory: %CD%

if exist "scripts\init_db.py" (
    echo Running database initialization...
    %PYTHON_PATH% scripts\init_db.py
    if %errorlevel% neq 0 (
        call :HandleError %LINENO% "Database initialization failed"
    )
) else (
    call :HandleError %LINENO% "init_db.py not found in scripts directory"
    echo Contents of scripts directory:
    dir scripts\ /b 2>nul || echo Scripts directory not found
)

if exist "scripts\setup_admin.py" (
    echo Setting up admin user...
    %PYTHON_PATH% scripts\setup_admin.py
    if %errorlevel% neq 0 (
        call :HandleError %LINENO% "Admin setup failed"
    )
) else (
    call :HandleError %LINENO% "setup_admin.py not found"
)

echo.
echo ✅ Database setup completed! 
echo.
echo Summary of errors found: %ErrorFound%
if "%ErrorFound%"=="1" (
    echo ⚠️ Some errors were encountered but ignored.
    echo The setup may still work. Continue? (y/n)
    set /p continue=
    if /i not "!continue!"=="y" exit /b 1
)

echo.
echo 🎉 Core setup completed successfully!
echo Press any key to continue with service installation...
pause >nul

echo.
echo 🔧 Service installation would continue from here...
echo (Stopping here for debugging - you can add the service installation part if this works)
echo.
echo Press any key to exit...
pause >nul