@echo off
echo ========================================
echo Packaging VS Code Extension
echo ========================================
echo.

echo [1/3] Checking if vsce is installed...
call vsce --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing vsce...
    call npm install -g @vscode/vsce
)
echo ✓ vsce is ready
echo.

echo [2/3] Packaging extension...
call vsce package
if %errorlevel% neq 0 (
    echo ERROR: Failed to package extension
    pause
    exit /b 1
)
echo ✓ Extension packaged successfully
echo.

echo [3/3] Package created!
echo.
echo ========================================
echo SUCCESS!
echo ========================================
echo.
echo Your extension package is ready:
dir /b *.vsix
echo.
echo To install:
echo   1. Open VS Code
echo   2. Extensions → ... → Install from VSIX
echo   3. Select the .vsix file
echo.
echo To distribute:
echo   - Share the .vsix file with users
echo   - Upload to GitHub releases
echo   - Publish to VS Code Marketplace
echo ========================================
echo.
pause
