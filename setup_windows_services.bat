@echo off
REM simple_debug.bat - Simple step-by-step installation - Updated for Official Python
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
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found
    echo Available Python commands:
    python3 --version 2>nul || echo python3: Not found
    py --version 2>nul || echo py: Not found
    echo.
    echo Please install Python 3.10 from python.org
    pause
    exit /b 1
)
echo ✅ Python OK
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
python -m pip install --upgrade pip
echo.
echo Installing requirements...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Requirements installation failed
    echo Trying individual packages...
    python -m pip install Flask==2.3.2
    python -m pip install Flask-SQLAlchemy==3.0.5
    python -m pip install Flask-CORS==4.0.0
    python -m pip install python-dotenv==1.0.0
    python -m pip install PyJWT==2.8.0
    python -m pip install Werkzeug==2.3.6
    python -m pip install bcrypt==4.0.1
    python -m pip install Pillow==10.0.0
)
echo.
echo Installing service dependencies...
python -m pip install pywin32 waitress
pause

REM Step 8: Test Flask
echo.
echo STEP 8: Testing Flask import...
python -c "import flask; print('✅ Flask version:', flask.__version__)"
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
    python scripts\init_db.py
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
    python scripts\setup_admin.py
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

REM Step 13: Fix run_backend.py (CORRECTED)
echo.
echo STEP 13: Creating/fixing run_backend.py...
cd /d "%SERVICE_DIR%"
echo # run_backend.py - Production backend runner for Windows service > run_backend.py
echo """Production Flask backend runner optimized for Windows services.""" >> run_backend.py
echo. >> run_backend.py
echo import os >> run_backend.py
echo import sys >> run_backend.py
echo from pathlib import Path >> run_backend.py
echo. >> run_backend.py
echo # Ensure we can find our modules >> run_backend.py
echo sys.path.insert(0, str(Path(__file__).parent)) >> run_backend.py
echo. >> run_backend.py
echo # Set production environment >> run_backend.py
echo os.environ['FLASK_ENV'] = 'production' >> run_backend.py
echo os.environ['FLASK_DEBUG'] = '0' >> run_backend.py
echo os.environ['UPLOAD_FOLDER'] = r'C:\Verificator Preturi App\assets' >> run_backend.py
echo. >> run_backend.py
echo def main(): >> run_backend.py
echo     """Run the Flask application in production mode.""" >> run_backend.py
echo     try: >> run_backend.py
echo         from app import create_app >> run_backend.py
echo         from waitress import serve >> run_backend.py
echo         print("🚀 Starting Campaign Manager Backend Service") >> run_backend.py
echo         print(f"📁 Assets folder: {os.environ['UPLOAD_FOLDER']}") >> run_backend.py
echo         print("🌐 Server will be available at: http://192.168.103.111:5000") >> run_backend.py
echo         >> run_backend.py
echo         # Create Flask app >> run_backend.py
echo         app = create_app() >> run_backend.py
echo         >> run_backend.py
echo         # Ensure assets folder exists >> run_backend.py
echo         assets_path = Path(os.environ['UPLOAD_FOLDER']) >> run_backend.py
echo         assets_path.mkdir(parents=True, exist_ok=True) >> run_backend.py
echo         >> run_backend.py
echo         print(f"✅ Assets folder ready: {assets_path}") >> run_backend.py
echo         print("🔄 Starting Waitress WSGI server...") >> run_backend.py
echo         >> run_backend.py
echo         # Use Waitress for production WSGI server >> run_backend.py
echo         serve( >> run_backend.py
echo             app, >> run_backend.py
echo             host='0.0.0.0',  # Listen on all interfaces >> run_backend.py
echo             port=5000, >> run_backend.py
echo             threads=4, >> run_backend.py
echo             channel_timeout=300, >> run_backend.py
echo             cleanup_interval=30, >> run_backend.py
echo             log_socket_errors=True >> run_backend.py
echo         ) >> run_backend.py
echo         >> run_backend.py
echo     except KeyboardInterrupt: >> run_backend.py
echo         print("\n🛑 Service stopped by user") >> run_backend.py
echo     except Exception as e: >> run_backend.py
echo         print(f"❌ Service failed to start: {e}") >> run_backend.py
echo         import traceback >> run_backend.py
echo         traceback.print_exc() >> run_backend.py
echo         sys.exit(1) >> run_backend.py
echo. >> run_backend.py
echo if __name__ == "__main__": >> run_backend.py
echo     main() >> run_backend.py
echo ✅ Created/fixed run_backend.py
pause

REM Step 14: Check serve_build.js exists (don't recreate)
echo.
echo STEP 14: Checking serve_build.js...
cd /d "%SERVICE_DIR%\campaign-manager-frontend"
if exist serve_build.js (
    echo ✅ serve_build.js already exists
) else (
    echo ❌ serve_build.js not found - this should have been created earlier
    pause
    exit /b 1
)
pause

REM Step 15: Test both services manually
echo.
echo STEP 15: Testing services manually...
echo.
echo Testing backend (will run for 10 seconds)...
cd /d "%SERVICE_DIR%"
timeout /t 2 /nobreak >nul
start /min python run_backend.py
timeout /t 8 /nobreak >nul
taskkill /f /im python.exe 2>nul
echo ✅ Backend test completed

echo.
echo Testing frontend (will run for 10 seconds)...
cd /d "%SERVICE_DIR%\campaign-manager-frontend"
start /min node serve_build.js
timeout /t 8 /nobreak >nul
taskkill /f /im node.exe 2>nul
echo ✅ Frontend test completed
pause

echo.
echo ✅ SETUP COMPLETED!
echo.
echo All components installed and tested!
echo Ready for Windows service installation.
echo.
echo Next steps:
echo 1. Install services: run install_services.bat
echo 2. Access app at: http://192.168.103.111:3000
echo 3. Login with: serban.damian@lensa.ro
echo.
pause