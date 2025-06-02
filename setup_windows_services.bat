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

REM Step 13: Create serve_build.js in frontend folder
echo.
echo STEP 13: Creating serve_build.js...
cd /d "%SERVICE_DIR%\campaign-manager-frontend"
if not exist serve_build.js (
    echo Creating serve_build.js...
    echo const express = require('express'); > serve_build.js
    echo const path = require('path'); >> serve_build.js
    echo const { createProxyMiddleware } = require('http-proxy-middleware'); >> serve_build.js
    echo. >> serve_build.js
    echo const app = express(); >> serve_build.js
    echo const PORT = 3000; >> serve_build.js
    echo const HOST = '0.0.0.0'; >> serve_build.js
    echo. >> serve_build.js
    echo console.log('🚀 Starting Campaign Manager Frontend Service'); >> serve_build.js
    echo console.log(`📁 Serving from: ${path.join(__dirname, 'dist')}`); >> serve_build.js
    echo console.log(`🌐 Frontend will be available at: http://192.168.103.111:${PORT}`); >> serve_build.js
    echo. >> serve_build.js
    echo app.use('/api', createProxyMiddleware({ >> serve_build.js
    echo     target: 'http://localhost:5000', >> serve_build.js
    echo     changeOrigin: true, >> serve_build.js
    echo     logLevel: 'info', >> serve_build.js
    echo     onError: (err, req, res) =^> { >> serve_build.js
    echo         console.error('Proxy Error:', err); >> serve_build.js
    echo         res.status(500).json({ error: 'Backend service unavailable' }); >> serve_build.js
    echo     } >> serve_build.js
    echo })); >> serve_build.js
    echo. >> serve_build.js
    echo app.use(express.static(path.join(__dirname, 'dist'))); >> serve_build.js
    echo. >> serve_build.js
    echo app.get('*', (req, res) =^> { >> serve_build.js
    echo     res.sendFile(path.join(__dirname, 'dist', 'index.html')); >> serve_build.js
    echo }); >> serve_build.js
    echo. >> serve_build.js
    echo app.use((err, req, res, next) =^> { >> serve_build.js
    echo     console.error('Server Error:', err); >> serve_build.js
    echo     res.status(500).json({ error: 'Internal server error' }); >> serve_build.js
    echo }); >> serve_build.js
    echo. >> serve_build.js
    echo const server = app.listen(PORT, HOST, () =^> { >> serve_build.js
    echo     console.log(`✅ Frontend service running on http://${HOST}:${PORT}`); >> serve_build.js
    echo     console.log('🔗 API requests will be proxied to backend on port 5000'); >> serve_build.js
    echo }); >> serve_build.js
    echo. >> serve_build.js
    echo process.on('SIGTERM', () =^> { >> serve_build.js
    echo     console.log('🛑 Received SIGTERM, shutting down gracefully'); >> serve_build.js
    echo     server.close(() =^> { >> serve_build.js
    echo         console.log('✅ Frontend service stopped'); >> serve_build.js
    echo         process.exit(0); >> serve_build.js
    echo     }); >> serve_build.js
    echo }); >> serve_build.js
    echo ✅ Created serve_build.js
) else (
    echo ✅ serve_build.js already exists
)
pause

REM Step 14: Create run_backend.py in root
echo.
echo STEP 14: Creating run_backend.py...
cd /d "%SERVICE_DIR%"
if not exist run_backend.py (
    echo Creating run_backend.py...
    echo import os > run_backend.py
    echo import sys >> run_backend.py
    echo from pathlib import Path >> run_backend.py
    echo. >> run_backend.py
    echo # Set production environment >> run_backend.py
    echo os.environ['FLASK_ENV'] = 'production' >> run_backend.py
    echo os.environ['FLASK_DEBUG'] = '0' >> run_backend.py
    echo os.environ['UPLOAD_FOLDER'] = r'C:\Verificator Preturi App\assets' >> run_backend.py
    echo. >> run_backend.py
    echo def main(): >> run_backend.py
    echo     try: >> run_backend.py
    echo         from app import create_app >> run_backend.py
    echo         from waitress import serve >> run_backend.py
    echo         print("🚀 Starting Campaign Manager Backend Service") >> run_backend.py
    echo         print(f"📁 Assets folder: {os.environ['UPLOAD_FOLDER']}") >> run_backend.py
    echo         print("🌐 Server will be available at: http://192.168.103.111:5000") >> run_backend.py
    echo         app = create_app() >> run_backend.py
    echo         assets_path = Path(os.environ['UPLOAD_FOLDER']) >> run_backend.py
    echo         assets_path.mkdir(parents=True, exist_ok=True) >> run_backend.py
    echo         print(f"✅ Assets folder ready: {assets_path}") >> run_backend.py
    echo         print("🔄 Starting Waitress WSGI server...") >> run_backend.py
    echo         serve(app, host='0.0.0.0', port=5000, threads=4) >> run_backend.py