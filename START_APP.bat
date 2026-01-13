@echo off
title RoWordNet Similarity
color 0A

echo.
echo  ====================================================
echo  ^|                                                  ^|
echo  ^|        RoWordNet Similarity Application          ^|
echo  ^|                                                  ^|
echo  ====================================================
echo.

:: Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: ============================================
:: TRY TO FIND PYTHON
:: ============================================

:: First check if Python is already available (regular install or activated env)
python --version >nul 2>&1
if not errorlevel 1 (
    echo  [OK] Python found in PATH
    goto :python_ok
)

:: Try to activate a local venv if it exists
if exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    echo  [*] Activating local venv...
    call "%SCRIPT_DIR%venv\Scripts\activate.bat"
    goto :check_python
)

:: Try to activate conda base
call conda activate base >nul 2>&1
if not errorlevel 1 (
    echo  [OK] Conda base activated
    goto :python_ok
)

:: Try common conda paths
for %%P in (
    "%USERPROFILE%\anaconda3\Scripts\activate.bat"
    "%USERPROFILE%\miniconda3\Scripts\activate.bat"
    "C:\ProgramData\anaconda3\Scripts\activate.bat"
    "C:\ProgramData\miniconda3\Scripts\activate.bat"
    "%LOCALAPPDATA%\anaconda3\Scripts\activate.bat"
    "%LOCALAPPDATA%\miniconda3\Scripts\activate.bat"
) do (
    if exist %%P (
        echo  [*] Found conda at %%P
        call %%P
        goto :check_python
    )
)

:check_python
python --version >nul 2>&1
if errorlevel 1 (
    goto :python_error
)

:python_ok
echo  [OK] Python version:
python --version
echo.

:: ============================================
:: CHECK NODE.JS
:: ============================================
node --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  [ERROR] Node.js is not installed!
    echo.
    echo  Please install Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo  [OK] Node.js version:
node --version
echo.

:: ============================================
:: INSTALL DEPENDENCIES IF NEEDED
:: ============================================

:: Check backend dependencies
cd /d "%SCRIPT_DIR%backend"
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo  [*] Installing Python dependencies...
    pip install -r requirements.txt
    echo.
)

:: Check frontend dependencies
cd /d "%SCRIPT_DIR%frontend"
if not exist "node_modules" (
    echo  [*] Installing Node.js dependencies...
    call npm install
    echo.
)

:: ============================================
:: START SERVERS
:: ============================================
echo  [*] Starting Backend Server (port 8000)...
cd /d "%SCRIPT_DIR%backend"
start /b "" python -m uvicorn main:app --host 127.0.0.1 --port 8000

timeout /t 4 /nobreak >nul

echo  [*] Starting Frontend Server (port 3000)...
cd /d "%SCRIPT_DIR%frontend"
start /b "" cmd /c "npm run dev"

timeout /t 8 /nobreak >nul

echo  [*] Opening browser...
start http://localhost:3000

echo.
echo  ====================================================
echo  ^|                                                  ^|
echo  ^|    Application is running!                      ^|
echo  ^|                                                  ^|
echo  ^|    Frontend: http://localhost:3000              ^|
echo  ^|    Backend:  http://localhost:8000              ^|
echo  ^|                                                  ^|
echo  ^|    CLOSE THIS WINDOW TO STOP THE APPLICATION    ^|
echo  ^|                                                  ^|
echo  ====================================================
echo.

:: Keep window open (closing it stops the servers)
:loop
timeout /t 5 /nobreak >nul
goto loop

:: ============================================
:: ERROR HANDLERS
:: ============================================
:python_error
color 0C
echo.
echo  [ERROR] Python is not installed or not found!
echo.
echo  Please install Python using one of these methods:
echo.
echo  1. Regular Python: https://www.python.org/downloads/
echo     (Make sure to check "Add Python to PATH")
echo.
echo  2. Anaconda: https://www.anaconda.com/download
echo.
echo  3. Miniconda: https://docs.conda.io/en/latest/miniconda.html
echo.
pause
exit /b 1
