# AI Code Assistant - VS Code Extension

A powerful VS Code extension that integrates your Hybrid AI Code Assistant directly into your editor with right-click context menu support.

## Features

🤖 **Right-Click Context Menu** - Select code and right-click to access AI features:
- 💡 **Explain Code** - Get detailed explanations of selected code
- 📚 **Generate Documentation** - Create Google-style docstrings
- 🔧 **Fix Bugs** - Automatically detect and fix bugs
- ⚡ **Optimize Code** - Improve performance and readability
- 🧪 **Generate Tests** - Create comprehensive unit tests

## Prerequisites

1. **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
2. **VS Code** (v1.80 or higher)
3. **AI Assistant Backend** running on `http://localhost:5000`

## Installation

### Step 1: Install Dependencies

```bash
cd vscode-extension
npm install
```

### Step 2: Start the Backend Server

In a separate terminal, start your AI Assistant backend:

```bash
cd ..
python frontend/app.py
```

Wait for the message: `✅ Model loaded successfully!`

### Step 3: Run the Extension

1. Open the `vscode-extension` folder in VS Code
2. Press `F5` to launch Extension Development Host
3. A new VS Code window will open with the extension loaded

## Usage

### Method 1: Right-Click Context Menu (Recommended)

1. **Select code** in your Python file
2. **Right-click** on the selection
3. Choose **"🤖 AI Code Assistant"** from the menu
4. Select the desired action:
   - Explain Code
   - Generate Documentation
   - Fix Bugs
   - Optimize Code
   - Generate Tests

### Method 2: Command Palette

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "AI Assistant"
3. Select the desired command

### Method 3: Keyboard Shortcuts (Optional)

You can add custom keybindings in VS Code settings:

```json
{
  "key": "ctrl+alt+e",
  "command": "aiCodeAssistant.explain"
},
{
  "key": "ctrl+alt+d",
  "command": "aiCodeAssistant.document"
}
```

## Configuration

Access settings via: `File > Preferences > Settings > AI Code Assistant`

### Available Settings

- **Server URL**: Backend server address (default: `http://localhost:5000`)
- **Show In New Editor**: Open results in new tab instead of replacing selection (default: `false`)

## How It Works

### For Explanations & Documentation
- Results open in a **new editor tab** beside your code
- Formatted as Markdown for easy reading

### For Bug Fixes & Optimizations
- **Default**: Replaces your selected code with the improved version
- **Alternative**: Enable "Show In New Editor" to compare side-by-side
- Explanations appear in the Output panel

### For Test Generation
- Opens generated tests in a new Python file
- Ready to save and run immediately

## Example Workflow

```python
# 1. Write or select buggy code
def find_max(numbers):
    max_val = 0  # Bug: doesn't work for negative numbers
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

# 2. Select the function
# 3. Right-click → AI Code Assistant → Fix Bugs
# 4. Code is automatically replaced with:

def find_max(numbers):
    """Find the maximum value in a list of numbers."""
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val
```

## Troubleshooting

### "Cannot connect to AI Assistant server"
- Ensure backend is running: `python frontend/app.py`
- Check server URL in settings matches your backend
- Verify port 5000 is not blocked by firewall

### "No active editor found"
- Make sure you have a file open in the editor
- Click inside the editor before using commands

### Extension not appearing in context menu
- Reload VS Code window: `Ctrl+Shift+P` → "Reload Window"
- Check that extension is activated (status bar shows "🤖 AI Assistant")

## Development

### Project Structure
```
vscode-extension/
├── extension.js       # Main extension logic
├── package.json       # Extension manifest
├── README.md          # This file
└── .vscodeignore     # Files to exclude from package
```

### Building for Distribution

```bash
npm install -g vsce
vsce package
```

This creates a `.vsix` file that can be installed in VS Code.

## Features Comparison

| Feature | Web Interface | VS Code Extension |
|---------|--------------|-------------------|
| Code Explanation | ✅ | ✅ |
| Documentation | ✅ | ✅ |
| Bug Fixing | ✅ | ✅ (with auto-replace) |
| Optimization | ✅ | ✅ (with auto-replace) |
| Test Generation | ✅ | ✅ |
| Right-click menu | ❌ | ✅ |
| Inline replacement | ❌ | ✅ |
| Side-by-side view | ❌ | ✅ |

## Keyboard Shortcuts Reference

| Action | Windows/Linux | Mac |
|--------|--------------|-----|
| Command Palette | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| Run Extension (Dev) | `F5` | `F5` |

## License

MIT License - See main project for details

## Support

For issues or questions:
1. Check the Output panel: `View > Output > AI Assistant`
2. Check backend logs in the terminal
3. Verify backend is responding: Visit `http://localhost:5000/api/status`

---

**Made with ❤️ using Hybrid AI (Fine-tuned CodeT5 + Gemini)**
