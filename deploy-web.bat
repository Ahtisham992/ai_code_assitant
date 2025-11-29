@echo off
echo ========================================
echo Web Interface Deployment Preparation
echo ========================================
echo.

echo [1/4] Activating virtual environment...
call .venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

echo [2/4] Updating requirements.txt...
pip freeze > requirements.txt
echo ✓ Requirements updated
echo.

echo [3/4] Installing gunicorn (for production)...
pip install gunicorn
pip freeze > requirements.txt
echo ✓ Gunicorn installed
echo.

echo [4/4] Creating deployment files...

REM Create Procfile for Heroku
echo web: gunicorn frontend.app:app > Procfile
echo ✓ Procfile created

REM Create runtime.txt
echo python-3.11.0 > runtime.txt
echo ✓ runtime.txt created

REM Create .dockerignore
(
echo .venv/
echo __pycache__/
echo *.pyc
echo .git/
echo .gitignore
echo *.md
echo vscode-extension/
) > .dockerignore
echo ✓ .dockerignore created

echo.
echo ========================================
echo SUCCESS! Files Ready for Deployment
echo ========================================
echo.
echo Created files:
echo   - requirements.txt (Python dependencies)
echo   - Procfile (Heroku configuration)
echo   - runtime.txt (Python version)
echo   - .dockerignore (Docker exclusions)
echo.
echo Next steps:
echo.
echo Option 1 - Deploy to Railway (Easiest):
echo   1. Go to https://railway.app/
echo   2. New Project → Deploy from GitHub
echo   3. Connect your repository
echo   4. Add environment variable: GEMINI_API_KEY
echo   5. Deploy automatically!
echo.
echo Option 2 - Deploy to Heroku:
echo   1. Install Heroku CLI
echo   2. heroku login
echo   3. heroku create your-app-name
echo   4. heroku config:set GEMINI_API_KEY=your_key
echo   5. git push heroku main
echo.
echo Option 3 - Deploy to Render:
echo   1. Go to https://render.com/
echo   2. New → Web Service
echo   3. Connect GitHub repository
echo   4. Build: pip install -r requirements.txt
echo   5. Start: gunicorn frontend.app:app
echo.
echo ========================================
pause
