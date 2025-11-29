# VS Code Extension Setup Guide

## Quick Start (5 Minutes)

### Step 1: Install Node.js Dependencies
```bash
cd vscode-extension
npm install
```

This installs:
- `vscode` - VS Code extension API
- `axios` - HTTP client for backend communication

### Step 2: Start Backend Server

Open a **new terminal** and run:
```bash
cd ..
python frontend/app.py
```

Wait for:
```
✅ Model loaded successfully!
🌐 Starting web server...
🔗 Open: http://localhost:5000
```

### Step 3: Test the Extension

1. **Open VS Code** in the `vscode-extension` folder
2. **Press F5** - This launches "Extension Development Host"
3. A **new VS Code window** opens with your extension loaded
4. Open any Python file in the new window
5. **Select some code** → **Right-click** → **"🤖 AI Code Assistant"**

## Detailed Walkthrough

### Testing Each Feature

#### 1. Explain Code
```python
# Select this code and right-click → AI Assistant → Explain Code
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
```

**Expected**: Opens explanation in new tab beside your code

#### 2. Generate Documentation
```python
# Select this function → Right-click → Generate Documentation
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count
```

**Expected**: Shows Google-style docstring with Args and Returns

#### 3. Fix Bugs
```python
# This has a bug! Select and use Fix Bugs
def find_max(numbers):
    max_val = 0  # Bug: fails for negative numbers
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val
```

**Expected**: Code is replaced with fixed version

#### 4. Optimize Code
```python
# Inefficient code - Select and use Optimize
def find_common(list1, list2):
    common = []
    for item in list1:
        if item in list2 and item not in common:
            common.append(item)
    return common
```

**Expected**: Replaced with optimized version using sets

#### 5. Generate Tests
```python
# Select this function → Generate Tests
def add_numbers(a, b):
    return a + b
```

**Expected**: Opens pytest tests in new file

## Configuration Options

### Change Server URL

If your backend runs on a different port:

1. `File > Preferences > Settings`
2. Search: "AI Code Assistant"
3. Change **Server URL** to your backend address

### Change Result Display Mode

**Option 1: Replace Selection (Default)**
- Fixed/optimized code replaces your selection
- Good for quick fixes

**Option 2: Show in New Editor**
- Results open in new tab
- Good for comparing before/after
- Enable: Settings → "Show In New Editor" → ✓

## Keyboard Shortcuts (Optional)

Add to `keybindings.json`:

```json
[
  {
    "key": "ctrl+alt+e",
    "command": "aiCodeAssistant.explain",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+alt+d",
    "command": "aiCodeAssistant.document",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+alt+f",
    "command": "aiCodeAssistant.fixBug",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+alt+o",
    "command": "aiCodeAssistant.optimize",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+alt+t",
    "command": "aiCodeAssistant.generateTests",
    "when": "editorTextFocus"
  }
]
```

## Troubleshooting

### Problem: "Cannot connect to AI Assistant server"

**Solution**:
1. Check backend is running: `python frontend/app.py`
2. Visit `http://localhost:5000/api/status` in browser
3. Should see: `{"loaded": true, "gemini_available": true}`

### Problem: Context menu doesn't show "AI Assistant"

**Solution**:
1. Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"
2. Check status bar shows "🤖 AI Assistant"
3. Try right-clicking on **selected text** (not empty space)

### Problem: "No active editor found"

**Solution**:
- Open a file first
- Click inside the editor
- Select some code before right-clicking

### Problem: Extension not loading

**Solution**:
1. Check `package.json` has no syntax errors
2. Run `npm install` again
3. Close and reopen VS Code
4. Press F5 again

## Building for Production

### Create Installable Package

```bash
# Install packaging tool
npm install -g vsce

# Create .vsix file
vsce package
```

This creates `ai-code-assistant-1.0.0.vsix`

### Install in VS Code

1. Open VS Code
2. `Extensions` → `...` (menu) → `Install from VSIX...`
3. Select the `.vsix` file
4. Reload VS Code

Now the extension is permanently installed!

## Development Tips

### Debugging the Extension

1. Set breakpoints in `extension.js`
2. Press F5 to launch Extension Development Host
3. Trigger a command (e.g., right-click → Explain)
4. Debugger pauses at breakpoints

### View Extension Logs

- `View > Output > Extension Host`
- Shows console.log() from extension.js

### View Backend Logs

- Check terminal where `app.py` is running
- Shows API requests and responses

## Architecture

```
┌─────────────────┐
│   VS Code       │
│   Extension     │
│  (extension.js) │
└────────┬────────┘
         │ HTTP POST
         │ /api/process
         ▼
┌─────────────────┐
│  Flask Backend  │
│    (app.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Hybrid AI Model │
│ (CodeT5+Gemini) │
└─────────────────┘
```

## Next Steps

1. ✅ Test all 5 features with different code samples
2. ✅ Try both display modes (replace vs new editor)
3. ✅ Add custom keyboard shortcuts
4. ✅ Package as .vsix for distribution
5. ✅ Share with team members!

## Support

- Check `README.md` for feature documentation
- Backend issues: Check `frontend/app.py` logs
- Extension issues: Check VS Code Output panel
