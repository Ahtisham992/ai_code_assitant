# 🚀 Complete Deployment Guide

## Overview

This guide covers deploying both:
1. **VS Code Extension** - For distribution to users
2. **Web Interface** - For online access

---

# Part 1: VS Code Extension Deployment

## Option A: Package as .VSIX (Recommended for Distribution)

### Step 1: Install VSCE (VS Code Extension Manager)

```bash
npm install -g @vscode/vsce
```

### Step 2: Update Extension Metadata

Edit `vscode-extension/package.json`:

```json
{
  "name": "ai-code-assistant",
  "displayName": "AI Code Assistant - Hybrid Model",
  "description": "Two-stage hybrid AI assistant (Fine-tuned CodeT5 + Gemini) for code explanation, documentation, bug fixing, and optimization",
  "version": "1.0.0",
  "publisher": "your-publisher-name",  // ← Change this!
  "icon": "icon.png",  // ← Add 128x128 icon (optional)
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/ai-code-assistant"
  },
  "keywords": [
    "ai",
    "code-assistant",
    "documentation",
    "bug-fix",
    "optimization",
    "gemini",
    "codet5"
  ],
  "license": "MIT"
}
```

### Step 3: Create Extension Icon (Optional but Recommended)

Create a 128x128 PNG icon named `icon.png` in `vscode-extension/` folder.

**Quick way**: Use an AI image generator or create a simple logo with:
- Robot emoji 🤖
- Code symbols <>
- AI theme colors (blue/purple)

### Step 4: Package the Extension

```bash
cd vscode-extension
vsce package
```

**Output**: `ai-code-assistant-1.0.0.vsix`

### Step 5: Test the Package

```bash
# Install in your VS Code
code --install-extension ai-code-assistant-1.0.0.vsix
```

## Option B: Publish to VS Code Marketplace (Public Distribution)

### Step 1: Create Azure DevOps Account

1. Go to: https://dev.azure.com/
2. Sign in with Microsoft account
3. Create organization (free)

### Step 2: Generate Personal Access Token (PAT)

1. In Azure DevOps: User Settings → Personal Access Tokens
2. Click "New Token"
3. Name: "VS Code Extension Publishing"
4. Organization: All accessible organizations
5. Scopes: **Marketplace → Manage**
6. Create token and **SAVE IT** (you won't see it again!)

### Step 3: Create Publisher

```bash
vsce create-publisher your-publisher-name
# Enter your PAT when prompted
```

### Step 4: Login

```bash
vsce login your-publisher-name
# Enter your PAT
```

### Step 5: Publish

```bash
cd vscode-extension
vsce publish
```

**Your extension is now live!** 🎉

Users can install via:
- VS Code Marketplace search
- Command: `ext install your-publisher-name.ai-code-assistant`

### Step 6: Update Extension

When you make changes:

```bash
# Increment version in package.json (1.0.0 → 1.0.1)
vsce publish patch  # or minor, or major
```

---

# Part 2: Web Interface Deployment

## Option A: Local/Development Deployment

### Step 1: Prepare Requirements

```bash
cd "d:\Software enginner\university\sem7\GenAI\GenAiProject"
pip freeze > requirements.txt
```

### Step 2: Create Startup Script

**Windows (`start_server.bat`):**
```batch
@echo off
echo Starting AI Code Assistant Server...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start Flask server
python frontend/app.py

pause
```

**Linux/Mac (`start_server.sh`):**
```bash
#!/bin/bash
echo "Starting AI Code Assistant Server..."

# Activate virtual environment
source .venv/bin/activate

# Start Flask server
python frontend/app.py
```

### Step 3: Run

```bash
# Windows
start_server.bat

# Linux/Mac
chmod +x start_server.sh
./start_server.sh
```

## Option B: Cloud Deployment (Production)

### Option B1: Deploy to Heroku (Free Tier Available)

#### Step 1: Install Heroku CLI

Download from: https://devcenter.heroku.com/articles/heroku-cli

#### Step 2: Create Heroku Files

**`Procfile`** (in project root):
```
web: gunicorn frontend.app:app
```

**`runtime.txt`** (in project root):
```
python-3.11.0
```

**Update `requirements.txt`**:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

#### Step 3: Initialize Git (if not already)

```bash
git init
git add .
git commit -m "Initial commit"
```

#### Step 4: Create Heroku App

```bash
heroku login
heroku create your-app-name
```

#### Step 5: Set Environment Variables

```bash
heroku config:set GEMINI_API_KEY=your_actual_api_key
```

#### Step 6: Deploy

```bash
git push heroku main
```

**Your app is live at**: `https://your-app-name.herokuapp.com`

#### Step 7: Scale (if needed)

```bash
heroku ps:scale web=1
```

### Option B2: Deploy to Railway (Easier than Heroku)

#### Step 1: Sign Up

Go to: https://railway.app/

#### Step 2: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub repository

#### Step 3: Configure

Railway auto-detects Python and Flask!

Add environment variable:
- Key: `GEMINI_API_KEY`
- Value: Your API key

#### Step 4: Deploy

Railway automatically deploys! 🎉

**Your app is live at**: `https://your-app.railway.app`

### Option B3: Deploy to Render (Free Tier)

#### Step 1: Sign Up

Go to: https://render.com/

#### Step 2: Create Web Service

1. New → Web Service
2. Connect GitHub repository
3. Configure:
   - **Name**: ai-code-assistant
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn frontend.app:app`

#### Step 3: Add Environment Variables

- `GEMINI_API_KEY`: Your API key

#### Step 4: Deploy

Click "Create Web Service"

**Your app is live!** 🎉

### Option B4: Deploy to Google Cloud Run (Scalable)

#### Step 1: Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 frontend.app:app
```

#### Step 2: Create `.dockerignore`

```
.venv/
__pycache__/
*.pyc
.git/
.gitignore
README.md
```

#### Step 3: Install Google Cloud CLI

Download from: https://cloud.google.com/sdk/docs/install

#### Step 4: Deploy

```bash
gcloud init
gcloud run deploy ai-code-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key
```

**Your app is live!** 🎉

---

# Part 3: Complete Production Setup

## Architecture

```
┌─────────────────────────────────────┐
│   VS Code Extension (Client)        │
│   - Distributed as .vsix            │
│   - Installed on user's machine     │
└──────────────┬──────────────────────┘
               │
               │ HTTPS
               ▼
┌─────────────────────────────────────┐
│   Backend API (Cloud Hosted)        │
│   - Heroku/Railway/Render/GCP       │
│   - Flask + Gunicorn                │
│   - Environment: GEMINI_API_KEY     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   AI Models                         │
│   - Fine-tuned CodeT5 (bundled)     │
│   - Gemini API (cloud)              │
└─────────────────────────────────────┘
```

## Configuration for Production

### Update Extension to Use Cloud Backend

Edit `vscode-extension/package.json`:

```json
"configuration": {
  "properties": {
    "aiCodeAssistant.serverUrl": {
      "type": "string",
      "default": "https://your-app.herokuapp.com",  // ← Cloud URL
      "description": "URL of the AI Code Assistant backend server"
    }
  }
}
```

### Add CORS to Backend

Edit `frontend/app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from extension
```

Install CORS:
```bash
pip install flask-cors
pip freeze > requirements.txt
```

---

# Part 4: Distribution Strategy

## For VS Code Extension

### Free Distribution
1. **GitHub Releases**:
   - Upload `.vsix` file to GitHub releases
   - Users download and install manually
   - Good for beta testing

2. **VS Code Marketplace**:
   - Free to publish
   - Searchable by all VS Code users
   - Automatic updates

### Paid Distribution
1. **Gumroad/Lemon Squeezy**:
   - Sell `.vsix` file
   - Simple payment processing
   - No marketplace fees

2. **License Key System**:
   - Extension checks license key with your API
   - Implement in `extension.js`

## For Web Interface

### Freemium Model
```
Free Tier:
- 10 requests per day
- Basic features only
- Web interface access

Pro Tier ($9.99/month):
- Unlimited requests
- All features
- VS Code extension access
- Priority support

Enterprise ($99/month):
- Team licenses
- Private model hosting
- Custom integration
- SLA support
```

### Implementation

Add rate limiting in `frontend/app.py`:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.headers.get('X-API-Key', 'anonymous'),
    default_limits=["10 per day"]  # Free tier
)

@app.route('/api/process', methods=['POST'])
@limiter.limit("100 per day")  # Pro tier (check API key)
def process_code():
    # ... existing code
```

---

# Part 5: Quick Deployment Checklist

## VS Code Extension
- [ ] Update `package.json` (publisher, description, keywords)
- [ ] Add icon.png (128x128)
- [ ] Test locally with F5
- [ ] Run `vsce package`
- [ ] Test .vsix installation
- [ ] Publish to marketplace OR distribute .vsix

## Web Interface
- [ ] Update `requirements.txt`
- [ ] Set GEMINI_API_KEY as environment variable
- [ ] Choose hosting platform (Heroku/Railway/Render)
- [ ] Deploy backend
- [ ] Test API endpoints
- [ ] Update extension's default serverUrl

## Documentation
- [ ] Update README with deployment info
- [ ] Add API documentation
- [ ] Create user guide
- [ ] Add troubleshooting section

---

# Part 6: Recommended Deployment Path

## For Quick Demo/Presentation (Today)

1. **Extension**: Package as .vsix
   ```bash
   cd vscode-extension
   npm install -g @vscode/vsce
   vsce package
   ```

2. **Web**: Keep running locally
   ```bash
   python frontend/app.py
   ```

3. **Demo**: Show both working together

## For Beta Testing (This Week)

1. **Extension**: Upload .vsix to GitHub releases
2. **Web**: Deploy to Railway (easiest, free)
3. **Share**: Give .vsix file + cloud URL to testers

## For Production (Next Month)

1. **Extension**: Publish to VS Code Marketplace
2. **Web**: Deploy to Google Cloud Run (scalable)
3. **Monetize**: Add Stripe for payments
4. **Support**: Set up help desk

---

# Part 7: Cost Estimation

## Free Tier (Good for 100-1000 users)

| Service | Cost | Limits |
|---------|------|--------|
| Railway | $0 | 500 hours/month |
| Render | $0 | 750 hours/month |
| Heroku | $0 | 550 hours/month |
| VS Code Marketplace | $0 | Unlimited |
| GitHub Releases | $0 | Unlimited |

## Paid Tier (1000+ users)

| Service | Cost/Month | Features |
|---------|-----------|----------|
| Railway Pro | $5 | Unlimited hours |
| Google Cloud Run | ~$10-50 | Auto-scaling |
| Heroku Hobby | $7 | Always on |
| Domain Name | $10-15 | Custom domain |

---

# Next Steps

Choose your deployment path:

**Option 1: Quick Demo** (30 minutes)
```bash
cd vscode-extension
vsce package
# Share .vsix file
```

**Option 2: Beta Release** (2 hours)
1. Package extension
2. Deploy to Railway
3. Update extension config
4. Share with testers

**Option 3: Full Production** (1 week)
1. Publish to VS Code Marketplace
2. Deploy to Google Cloud
3. Set up payment system
4. Launch marketing

Which path do you want to take? I can guide you through the specific steps!
