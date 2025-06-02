@echo off
REM simple_debug.bat - Simple step-by-step installation
echo ==========================================
echo Campaign Manager - Simple Setup Debug
echo ==========================================

REM Check admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Must run as Administrator
    pause
    exit /b 1
)
echo ✅ Running as Administrator

REM Step 1: Check Python
echo.
echo STEP 1: Checking Python...
python3.10 --version
if %errorlevel% neq 0 (
    echo ❌ Python 3.10 not found
    echo Available Python commands:
    python --version 2>nul || echo python: Not found
    python3 --version 2>nul || echo python3: Not found
    pause
    exit /b 1
)
echo ✅ Python 3.10 OK
pause

REM Step 2: Check Node
echo.
echo STEP 2: Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ❌ Node.js not found
    pause
    exit /b 1
)
echo ✅ Node.js OK
pause

REM Step 3: Check current directory
echo.
echo STEP 3: Checking current directory...
echo Current directory: %CD%
if exist app.py (
    echo ✅ app.py found
) else (
    echo ❌ app.py not found - are you in the right directory?
    echo Contents:
    dir /b
    pause
    exit /b 1
)

if exist requirements.txt (
    echo ✅ requirements.txt found
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

if exist campaign-manager-frontend (
    echo ✅ frontend folder found
) else (
    echo ❌ frontend folder not found
    pause
    exit /b 1
)
pause

REM Step 4: Create service directory
echo.
echo STEP 4: Creating service directory...
set SERVICE_DIR=C:\CampaignManager
if not exist "%SERVICE_DIR%" (
    mkdir "%SERVICE_DIR%"
    echo ✅ Created %SERVICE_DIR%
) else (
    echo ✅ Directory exists %SERVICE_DIR%
)
pause

REM Step 5: Copy files
echo.
echo STEP 5: Copying files...
echo From: %CD%
echo To: %SERVICE_DIR%
xcopy /E /I /Y "%CD%\*" "%SERVICE_DIR%\"
if %errorlevel% neq 0 (
    echo ❌ Copy failed with error level: %errorlevel%
    pause
    exit /b 1
)
echo ✅ Files copied
pause

REM Step 6: Change to service directory
echo.
echo STEP 6: Changing to service directory...
cd /d "%SERVICE_DIR%"
echo Now in: %CD%
if exist app.py (
    echo ✅ app.py found in service directory
) else (
    echo ❌ app.py not found after copy
    echo Contents:
    dir /b
    pause
    exit /b 1
)
pause

REM Step 7: Install Python dependencies
echo.
echo STEP 7: Installing Python dependencies...
echo Upgrading pip...
python3.10 -m pip install --upgrade pip
echo.
echo Installing requirements...
python3.10 -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Requirements installation failed
    echo Trying individual packages...
    python3.10 -m pip install Flask==2.3.2
    python3.10 -m pip install Flask-SQLAlchemy==3.0.5
    python3.10 -m pip install Flask-CORS==4.0.0
    python3.10 -m pip install python-dotenv==1.0.0
    python3.10 -m pip install PyJWT==2.8.0
    python3.10 -m pip install Werkzeug==2.3.6
    python3.10 -m pip install bcrypt==4.0.1
    python3.10 -m pip install Pillow==10.0.0
)
echo.
echo Installing service dependencies...
python3.10 -m pip install pywin32 waitress
pause

REM Step 8: Test Flask
echo.
echo STEP 8: Testing Flask import...
python3.10 -c "import flask; print('✅ Flask version:', flask.__version__)"
if %errorlevel% neq 0 (
    echo ❌ Flask import failed
    pause
    exit /b 1
)
echo ✅ Flask import OK
pause

REM Step 9: Setup frontend
echo.
echo STEP 9: Setting up frontend...
cd campaign-manager-frontend
if %errorlevel% neq 0 (
    echo ❌ Frontend directory not found
    cd /d "%SERVICE_DIR%"
    dir /b
    pause
    exit /b 1
)
echo ✅ In frontend directory: %CD%

REM Fix PostCSS config
echo Creating fixed PostCSS config...
echo module.exports = { > postcss.config.js
echo   plugins: { >> postcss.config.js
echo     tailwindcss: {}, >> postcss.config.js
echo     autoprefixer: {}, >> postcss.config.js
echo   }, >> postcss.config.js
echo } >> postcss.config.js
echo ✅ PostCSS config fixed
pause

REM Step 10: Install frontend dependencies
echo.
echo STEP 10: Installing frontend dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ❌ npm install failed, trying with legacy peer deps...
    call npm install --legacy-peer-deps
)
echo.
echo Installing express dependencies...
call npm install express http-proxy-middleware
pause

REM Step 11: Build frontend
echo.
echo STEP 11: Building frontend...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Build failed
    echo Check the error messages above
    pause
) else (
    echo ✅ Build successful
)
pause

REM Step 12: Database setup
echo.
echo STEP 12: Setting up database...
cd /d "%SERVICE_DIR%"
echo Current directory: %CD%

if exist scripts\init_db.py (
    echo Running database initialization...
    python3.10 scripts\init_db.py
    if %errorlevel% neq 0 (
        echo ❌ Database init failed
        pause
    ) else (
        echo ✅ Database initialized
    )
) else (
    echo ❌ scripts\init_db.py not found
    echo Contents of scripts directory:
    dir scripts\ 2>nul || echo Scripts directory not found
    pause
)

if exist scripts\setup_admin.py (
    echo Setting up admin user...
    python3.10 scripts\setup_admin.py
    if %errorlevel% neq 0 (
        echo ❌ Admin setup failed
        pause
    ) else (
        echo ✅ Admin user created
    )
) else (
    echo ❌ scripts\setup_admin.py not found
    pause
)

echo.
echo ✅ SETUP COMPLETED!
echo.
echo Next steps:
echo 1. Test backend manually: python3.10 run_backend.py
echo 2. Test frontend manually: cd campaign-manager-frontend && node serve_build.js
echo 3. If both work, we can set up the Windows services
echo.
pause