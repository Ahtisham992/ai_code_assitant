# 🔑 Gemini API Setup Guide

## Problem: Gemini Not Working

Your system shows:
- ✅ google-genai package installed (v1.52.0)
- ❌ GEMINI_API_KEY not set
- ❌ AI features showing "AI: Limited" instead of "AI: Active"

---

## Solution: Set Up Gemini API Key

### Step 1: Get Free API Key (2 minutes)

1. **Go to**: https://aistudio.google.com/app/apikey
2. **Sign in** with your Google account
3. **Click**: "Create API Key"
4. **Copy** the key (looks like: `AIzaSyD...`)

---

### Step 2: Set Environment Variable

#### **Windows PowerShell** (Your System)

```powershell
# Set for current session
$env:GEMINI_API_KEY = "YOUR_API_KEY_HERE"

# Verify it's set
echo $env:GEMINI_API_KEY

# Set permanently (recommended)
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'YOUR_API_KEY_HERE', 'User')
```

#### **Windows CMD**
```cmd
set GEMINI_API_KEY=YOUR_API_KEY_HERE
```

#### **Linux/Mac**
```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"

# Add to ~/.bashrc or ~/.zshrc for permanent
echo 'export GEMINI_API_KEY="YOUR_API_KEY_HERE"' >> ~/.bashrc
```

---

### Step 3: Restart Your Application

```powershell
# Stop current server (Ctrl+C)

# Restart
cd frontend
python app.py
```

---

### Step 4: Verify It Works

**You should see:**
```
Loading fine-tuned model from ./models/finetuned_model...
✅ Fine-tuned model loaded on cpu
✅ Google Gemini initialized (FREE) - Using gemini-2.5-flash
Initializing codebase retrieval...
✅ Codebase retrieval ready
✅ Model loaded successfully!
✅ Gemini available: True
```

**In the web interface:**
- Status: "✅ System ready!"
- Badge: "AI: Active" (green)

---

## Alternative: Run Without Gemini

If you can't get Gemini API key, the system still works with:
- ✅ Code Explanation (fine-tuned model only)
- ✅ Documentation (fine-tuned model only)
- ⚠️ Bug Fix (limited - fine-tuned model)
- ⚠️ Optimization (not available)
- ⚠️ Test Generation (not available)

---

## Troubleshooting

### Issue 1: "API key invalid"
**Solution:** 
- Check key has no extra spaces
- Regenerate key at https://aistudio.google.com/app/apikey
- Make sure you're using the correct Google account

### Issue 2: "Model not found"
**Solution:**
- Gemini models change names sometimes
- The code tries 3 models automatically:
  1. gemini-2.5-flash
  2. gemini-2.0-flash
  3. gemini-2.5-flash-lite

### Issue 3: "Rate limit exceeded"
**Solution:**
- Free tier: 60 requests/minute
- Wait 1 minute and try again
- Consider upgrading to paid tier

### Issue 4: Environment variable not persisting
**Solution (Windows):**
```powershell
# Set system-wide (requires admin)
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'YOUR_KEY', 'Machine')

# Or add to Windows Environment Variables:
# 1. Search "Environment Variables" in Windows
# 2. Click "Environment Variables" button
# 3. Under "User variables", click "New"
# 4. Variable name: GEMINI_API_KEY
# 5. Variable value: YOUR_API_KEY
# 6. Click OK
# 7. Restart PowerShell/CMD
```

---

## Quick Test

```powershell
# Test if Gemini works
python -c "import os; from google import genai; client = genai.Client(api_key=os.getenv('GEMINI_API_KEY')); print(client.models.generate_content(model='gemini-2.5-flash', contents='Hello').text)"
```

**Expected output:** A response from Gemini

---

## What Each Feature Uses

| Feature | Fine-tuned Model | Gemini AI | Works Without Gemini? |
|---------|------------------|-----------|----------------------|
| **Explain** | ✅ Base analysis | ✅ Enhanced | ✅ Yes (basic) |
| **Document** | ✅ Base docs | ✅ Enhanced | ✅ Yes (basic) |
| **Fix Bugs** | ⚠️ Limited | ✅ Main | ⚠️ Limited |
| **Optimize** | ❌ No | ✅ Yes | ❌ No |
| **Tests** | ❌ No | ✅ Yes | ❌ No |
| **RAG Context** | ✅ Retrieval | ✅ Enhancement | ✅ Yes (basic) |

---

## Cost

**Gemini API Pricing (as of Nov 2025):**
- **Free Tier**: 60 requests/minute, 1500 requests/day
- **Paid Tier**: $0.00025 per 1K characters (~$0.25 per 1M chars)

**Your Usage:**
- Average request: ~500 characters
- Cost per request: ~$0.000125 (basically free!)
- 1000 requests = $0.125 (12.5 cents)

---

## Next Steps

1. ✅ Get API key from https://aistudio.google.com/app/apikey
2. ✅ Set `GEMINI_API_KEY` environment variable
3. ✅ Restart your Flask server
4. ✅ Test all 5 features
5. ✅ Index your codebase for RAG features

---

**Need Help?**
- Gemini API Docs: https://ai.google.dev/docs
- Get API Key: https://aistudio.google.com/app/apikey
- Check Status: https://status.cloud.google.com/
