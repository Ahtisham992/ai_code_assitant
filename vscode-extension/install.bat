@echo off
echo ========================================
echo AI Code Assistant - VS Code Extension
echo Installation Script
echo ========================================
echo.

echo [1/3] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please download and install Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo ✓ Node.js is installed
echo.

echo [2/3] Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed successfully
echo.

echo [3/3] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Start the backend server:
echo    cd ..
echo    python frontend/app.py
echo.
echo 2. Open this folder in VS Code
echo.
echo 3. Press F5 to launch the extension
echo.
echo 4. Right-click on code to use AI features!
echo ========================================
echo.
pause
